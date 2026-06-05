"""图谱读写服务。

GraphService 是 graph.json 的主要访问入口，负责：
- 读取和保存完整图谱
- 查询节点、边和邻居
- 按稳定规则生成节点/边 ID
- 按 type+name、source+target+relation+业务键 去重
- 通过图谱级事务、WAL 和内存索引保护并发写入

注意：这里不直接调用 LLM。LLM 生成的候选数据由 ExpansionService 校验后再通过本服务写入。
"""

import hashlib
import re
from datetime import datetime
from dataclasses import dataclass
from threading import RLock
from typing import Any, Callable, TypeVar

from app.core.errors import NotFoundError
from app.core.json_store import append_jsonl, read_json, read_jsonl, truncate_file, write_json
from app.core.paths import GRAPH_EDGES_FILE, GRAPH_META_FILE, GRAPH_NODES_FILE, GRAPH_WAL_FILE
from app.models.graph import GraphData, GraphEdge, GraphMetadata, GraphNode

T = TypeVar("T")


def now_iso() -> str:
    """返回秒级 UTC 时间字符串，用于 metadata 和索引更新时间。"""
    return datetime.utcnow().replace(microsecond=0).isoformat()


def to_snake_case(text: str) -> str:
    """将 PascalCase 节点类型转换为 snake_case，作为 ID 前缀。"""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def short_hash(value: str) -> str:
    """生成短 hash，保证 ID 稳定且长度适中。"""
    return hashlib.md5(value.encode("utf-8")).hexdigest()[:8]


def generate_node_id(node_type: str, name: str, parent_node_id: str | None = None) -> str:
    """根据节点类型、名称和父节点生成稳定节点 ID。

    parent_node_id 参与 hash，可让同名候选节点在不同扩展上下文下保持可区分。
    """
    prefix = to_snake_case(node_type)
    raw = f"{node_type}:{name}:{parent_node_id or ''}"
    return f"{prefix}_{short_hash(raw)}"


def _business_value(properties: dict[str, Any]) -> str | None:
    """Extract the explicit business key that makes a relation unique."""
    for key in ("timestamp", "observed_at", "time", "event_id", "observation_id"):
        value = properties.get(key)
        if value not in (None, ""):
            return f"{key}={value}"
    return None


def edge_business_key(edge: GraphEdge) -> str:
    """Return the edge business key used for multi-edge dedupe."""
    return _business_value(edge.properties) or ""


def edge_dedupe_key(source: str, target: str, relation: str, business_key: str = "") -> str:
    """Build the stable edge dedupe key."""
    return f"{source}:{target}:{relation}:{business_key}"


def generate_edge_id(source: str, relation: str, target: str, properties: dict[str, Any] | None = None) -> str:
    """根据 source、relation、target 和显式业务键生成稳定边 ID。"""
    business_key = _business_value(properties or {}) or ""
    return f"edge_{short_hash(edge_dedupe_key(source, target, relation, business_key))}"


def node_type_name_key(node_type: str, name: str) -> str:
    """Normalize the node dedupe key."""
    return f"{node_type}:{name.strip().casefold()}"


@dataclass
class GraphIndex:
    """In-memory indexes derived from the current graph snapshot."""

    node_by_id: dict[str, GraphNode]
    node_by_type_name: dict[str, GraphNode]
    edge_by_id: dict[str, GraphEdge]
    edge_by_dedupe_key: dict[str, GraphEdge]


def build_graph_index(graph: GraphData) -> GraphIndex:
    """Build fast lookup indexes for the current graph."""
    return GraphIndex(
        node_by_id={node.id: node for node in graph.nodes},
        node_by_type_name={node_type_name_key(node.type, node.name): node for node in graph.nodes},
        edge_by_id={edge.id: edge for edge in graph.edges},
        edge_by_dedupe_key={
            edge_dedupe_key(edge.source, edge.target, edge.relation, edge_business_key(edge)): edge
            for edge in graph.edges
        },
    )


class GraphService:
    """封装 graph.json 的读写和基础查询。"""

    _graph_lock = RLock()
    _graph_cache: GraphData | None = None
    _index_cache: GraphIndex | None = None

    @classmethod
    def _copy_graph(cls, graph: GraphData) -> GraphData:
        """Return an isolated graph object so callers cannot mutate the cache."""
        return graph.model_copy(deep=True)

    @classmethod
    def _read_base_graph(cls) -> GraphData:
        """Read the compacted graph files from disk."""
        meta = read_json(GRAPH_META_FILE, {"graph_id": "ocean_kg_demo_v1", "version": 1})
        nodes_raw = read_json(GRAPH_NODES_FILE, [])
        edges_raw = read_json(GRAPH_EDGES_FILE, [])
        return GraphData(
            graph_id=meta.get("graph_id", "ocean_kg_demo_v1"),
            version=meta.get("version", 1),
            nodes=[GraphNode.model_validate(n) for n in nodes_raw],
            edges=[GraphEdge.model_validate(e) for e in edges_raw],
        )

    @classmethod
    def _dump_by_id(cls, items: list[GraphNode] | list[GraphEdge]) -> dict[str, dict[str, Any]]:
        """Serialize graph items by ID for change detection."""
        return {item.id: item.model_dump(mode="json") for item in items}

    @classmethod
    def _wal_records_for_change(cls, before: GraphData, after: GraphData, reason: str) -> list[dict[str, Any]]:
        """Create WAL records for changed nodes and edges."""
        before_nodes = cls._dump_by_id(before.nodes)
        before_edges = cls._dump_by_id(before.edges)
        records: list[dict[str, Any]] = []

        for node in after.nodes:
            payload = node.model_dump(mode="json")
            if before_nodes.get(node.id) != payload:
                records.append({"kind": "node_upsert", "node": payload})

        for edge in after.edges:
            payload = edge.model_dump(mode="json")
            if before_edges.get(edge.id) != payload:
                records.append({"kind": "edge_upsert", "edge": payload})

        if records:
            stamp = now_iso()
            for record in records:
                record.update({
                    "timestamp": stamp,
                    "reason": reason,
                    "graph_id": after.graph_id,
                    "version": after.version,
                })
        return records

    @classmethod
    def _apply_wal_records(cls, graph: GraphData, records: list[dict[str, Any]]) -> GraphData:
        """Replay WAL records idempotently over a compacted graph."""
        if not records:
            return graph

        node_by_id = {node.id: node for node in graph.nodes}
        edge_by_id = {edge.id: edge for edge in graph.edges}
        version = graph.version

        for record in records:
            kind = record.get("kind")
            if kind == "node_upsert":
                node = GraphNode.model_validate(record.get("node", {}))
                node_by_id[node.id] = node
            elif kind == "edge_upsert":
                edge = GraphEdge.model_validate(record.get("edge", {}))
                edge_by_id[edge.id] = edge
            version = max(version, int(record.get("version") or version))

        return GraphData(
            graph_id=graph.graph_id,
            version=version,
            nodes=list(node_by_id.values()),
            edges=list(edge_by_id.values()),
        )

    @classmethod
    def _load_current_locked(cls) -> GraphData:
        """Load compacted files plus any unapplied WAL records."""
        graph = cls._read_base_graph()
        graph = cls._apply_wal_records(graph, read_jsonl(GRAPH_WAL_FILE))
        cls._graph_cache = graph
        cls._index_cache = build_graph_index(graph)
        return graph

    @classmethod
    def _current_locked(cls) -> GraphData:
        """Return the current cached graph, loading it if needed."""
        if cls._graph_cache is None or cls._index_cache is None:
            return cls._load_current_locked()
        return cls._graph_cache

    @classmethod
    def _refresh_cache_locked(cls, graph: GraphData) -> None:
        """Refresh graph and index caches after a committed write."""
        cls._graph_cache = graph
        cls._index_cache = build_graph_index(graph)

    def load_graph(self) -> GraphData:
        """从内存快照读取图谱，必要时从主文件和 WAL 组装。"""
        with self._graph_lock:
            return self._copy_graph(self._current_locked())

    def save_graph(self, graph: GraphData) -> None:
        """将图谱分文件写入 meta.json、nodes.json、edges.json，并刷新索引。

        业务结构变更优先使用 apply_mutation；此方法保留给初始化脚本和数据重置脚本。
        """
        with self._graph_lock:
            write_json(GRAPH_META_FILE, {"graph_id": graph.graph_id, "version": graph.version})
            write_json(GRAPH_NODES_FILE, [n.model_dump(mode="json") for n in graph.nodes])
            write_json(GRAPH_EDGES_FILE, [e.model_dump(mode="json") for e in graph.edges])
            truncate_file(GRAPH_WAL_FILE)
            self._refresh_cache_locked(self._copy_graph(graph))

    def apply_mutation(self, reason: str, mutator: Callable[[GraphData], T]) -> tuple[T, GraphData]:
        """Run a graph read-modify-write sequence as one in-process transaction."""
        with self._graph_lock:
            before = self._copy_graph(self._load_current_locked())
            working = self._copy_graph(before)
            result = mutator(working)

            records = self._wal_records_for_change(before, working, reason)
            for record in records:
                append_jsonl(GRAPH_WAL_FILE, record)

            if records:
                write_json(GRAPH_META_FILE, {"graph_id": working.graph_id, "version": working.version})
                write_json(GRAPH_NODES_FILE, [n.model_dump(mode="json") for n in working.nodes])
                write_json(GRAPH_EDGES_FILE, [e.model_dump(mode="json") for e in working.edges])
                truncate_file(GRAPH_WAL_FILE)
                self._refresh_cache_locked(working)
            else:
                self._refresh_cache_locked(before)

            return result, self._copy_graph(self._current_locked())

    def get_graph(self) -> GraphData:
        """返回完整图谱。"""
        return self.load_graph()

    def get_node(self, node_id: str) -> GraphNode:
        """按节点 ID 查询节点，不存在则抛业务异常。"""
        with self._graph_lock:
            self._current_locked()
            node = self._index_cache.node_by_id.get(node_id) if self._index_cache else None
            if node:
                return node.model_copy(deep=True)
        raise NotFoundError(f"Node not found: {node_id}", code="NODE_NOT_FOUND")

    def get_edge(self, edge_id: str) -> GraphEdge:
        """按边 ID 查询边，不存在则抛业务异常。"""
        with self._graph_lock:
            self._current_locked()
            edge = self._index_cache.edge_by_id.get(edge_id) if self._index_cache else None
            if edge:
                return edge.model_copy(deep=True)
        raise NotFoundError(f"Edge not found: {edge_id}", code="EDGE_NOT_FOUND")

    def get_neighbors(self, node_id: str, depth: int = 1) -> dict[str, Any]:
        """查询节点邻居。

        使用简单广度扩展，depth 最多限制为 3，避免图谱较大时单次请求过重。
        返回值包含邻居节点和相关边。
        """
        graph = self.load_graph()
        if not any(node.id == node_id for node in graph.nodes):
            raise NotFoundError(f"Node not found: {node_id}", code="NODE_NOT_FOUND")

        depth = max(1, min(depth, 3))

        # 先构造 id -> node 字典，最后把 visited 的节点 ID 快速转回节点对象。
        node_by_id = {node.id: node for node in graph.nodes}

        # visited 防止环路导致重复扩展；frontier 是当前深度层要继续展开的节点集合。
        visited = {node_id}
        frontier = {node_id}
        neighbor_edges: list[GraphEdge] = []

        # 每一轮从当前 frontier 出发，收集相连边和下一层节点。
        for _ in range(depth):
            next_frontier: set[str] = set()
            for edge in graph.edges:
                # 只要边的一端在当前 frontier，就说明这条边连接到当前层。
                if edge.source in frontier or edge.target in frontier:
                    neighbor_edges.append(edge)

                    # 取边的另一端作为下一层候选节点。
                    other = edge.target if edge.source in frontier else edge.source
                    if other not in visited:
                        next_frontier.add(other)
                        visited.add(other)
            frontier = next_frontier

        # visited 包含中心节点自身；前端通常也需要中心节点来渲染局部图。
        neighbor_nodes = [node_by_id[node_id] for node_id in visited if node_id in node_by_id]
        return {"nodes": neighbor_nodes, "edges": neighbor_edges}

    def search_by_keywords(self, keywords: list[str]) -> dict[str, Any]:
        """根据关键词搜索图谱节点。

        在节点的 name 和 properties.description 中做子串匹配（不区分大小写）。
        返回匹配节点及其一跳邻居，用于构建 QA 上下文。
        """
        graph = self.load_graph()
        if not keywords or not graph.nodes:
            return {"nodes": [], "edges": [], "matched_nodes": []}

        # 将关键词统一小写，用于不区分大小写的匹配。
        kw_lower = [kw.lower() for kw in keywords]

        matched: list[GraphNode] = []
        for node in graph.nodes:
            name_lower = node.name.lower()
            desc_lower = (node.properties.get("description") or "").lower()
            for kw in kw_lower:
                if kw in name_lower or kw in desc_lower:
                    matched.append(node)
                    break

        if not matched:
            return {"nodes": [], "edges": [], "matched_nodes": []}

        # 收集匹配节点的 ID 集合，用于扩展邻居。
        matched_ids = {node.id for node in matched}

        # 构建 id -> node 索引。
        node_by_id = {node.id: node for node in graph.nodes}

        # 从匹配节点出发，收集一跳邻居。
        visited = set(matched_ids)
        related_edges: list[GraphEdge] = []
        for edge in graph.edges:
            if edge.source in matched_ids or edge.target in matched_ids:
                related_edges.append(edge)
                other = edge.target if edge.source in matched_ids else edge.source
                if other not in visited:
                    visited.add(other)

        all_nodes = [node_by_id[nid] for nid in visited if nid in node_by_id]
        return {"nodes": all_nodes, "edges": related_edges, "matched_nodes": [n.model_dump(mode="json") for n in matched]}

    def add_node(self, graph: GraphData, node: GraphNode) -> GraphNode:
        """向图谱添加节点。

        去重规则：type 相同且 name 相同即视为同一节点。
        返回最终存储的节点，可能是已有节点。
        """
        existing = self.find_similar_node(graph, node.type, node.name)
        if existing:
            # 去重命中时不增加版本号，因为图谱结构没有发生变化。
            return existing

        # 只有真正新增节点时才提升 graph.version。
        graph.nodes.append(node)
        graph.version += 1
        return node

    def add_edge(self, graph: GraphData, edge: GraphEdge) -> GraphEdge:
        """向图谱添加边。

        去重规则：source、target、relation 和显式业务键相同即视为同一条边。
        """
        existing = self.find_edge(
            graph,
            edge.source,
            edge.target,
            edge.relation,
            business_key=edge_business_key(edge),
        )
        if existing:
            # 已存在的边直接复用，避免重复关系污染图谱。
            return existing

        # 只有真正新增边时才提升 graph.version。
        graph.edges.append(edge)
        graph.version += 1
        return edge

    def find_similar_node(self, graph: GraphData, node_type: str, name: str) -> GraphNode | None:
        """按节点去重规则查找已有节点。"""
        return build_graph_index(graph).node_by_type_name.get(node_type_name_key(node_type, name))

    def find_edge(
        self,
        graph: GraphData,
        source: str,
        target: str,
        relation: str,
        business_key: str = "",
    ) -> GraphEdge | None:
        """按边去重规则查找已有边。"""
        key = edge_dedupe_key(source, target, relation, business_key)
        return build_graph_index(graph).edge_by_dedupe_key.get(key)

    def edge_exists(self, graph: GraphData, source: str, target: str, relation: str) -> bool:
        """判断某条边是否存在。"""
        return self.find_edge(graph, source, target, relation) is not None

    def mark_expanded(self, graph: GraphData, node_id: str, expand_type: str) -> None:
        """标记节点的某个扩展类型已完成。"""
        for node in graph.nodes:
            if node.id == node_id:
                # expanded 是按 expand_type 记录的布尔字典，便于前端展示扩展按钮状态。
                node.expanded[expand_type] = True
                node.metadata.updated_at = now_iso()
                return
        raise NotFoundError(f"Node not found: {node_id}", code="NODE_NOT_FOUND")

    def build_node(
        self,
        node_type: str,
        name: str,
        properties: dict[str, Any],
        parent_node_id: str | None = None,
        source: str = "generated",
    ) -> GraphNode:
        """根据候选节点数据构造后端正式节点。

        LLM 不允许提供最终 ID；这里统一生成 ID 和 metadata。
        """
        created_at = now_iso()
        return GraphNode(
            # ID 由后端稳定生成，保证同一候选在相同上下文中可重复得到相同 ID。
            id=generate_node_id(node_type, name, parent_node_id),
            type=node_type,
            name=name,
            properties=properties,
            metadata=GraphMetadata(
                # source 区分 seed/manual/generated，便于后续审计和展示。
                source=source,
                parent_node=parent_node_id,
                created_at=created_at,
                updated_at=created_at,
            ),
        )

    def build_edge(
        self,
        source: str,
        target: str,
        relation: str,
        weight: float,
        properties: dict[str, Any],
        parent_node_id: str | None = None,
        source_name: str = "generated",
    ) -> GraphEdge:
        """根据候选边数据构造后端正式边。"""
        created_at = now_iso()
        return GraphEdge(
            # 边 ID 由三元组和显式业务键生成，配合 add_edge 支持多重边。
            id=generate_edge_id(source, relation, target, properties),
            source=source,
            target=target,
            relation=relation,
            weight=weight,
            properties=properties,
            metadata=GraphMetadata(
                source=source_name,
                parent_node=parent_node_id,
                created_at=created_at,
                updated_at=created_at,
            ),
        )
