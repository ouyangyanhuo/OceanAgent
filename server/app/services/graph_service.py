"""图谱读写服务。

GraphService 是 graph.json 的主要访问入口，负责：
- 读取和保存完整图谱
- 查询节点、边和邻居
- 按稳定规则生成节点/边 ID
- 按 type+name、source+target+relation 去重

注意：这里不直接调用 LLM。LLM 生成的候选数据由 ExpansionService 校验后再通过本服务写入。
"""

import hashlib
import re
from datetime import datetime
from typing import Any

from app.core.errors import NotFoundError
from app.core.json_store import read_json, write_json
from app.core.paths import GRAPH_EDGES_FILE, GRAPH_META_FILE, GRAPH_NODES_FILE
from app.models.graph import GraphData, GraphEdge, GraphMetadata, GraphNode


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


def generate_edge_id(source: str, relation: str, target: str) -> str:
    """根据 source、relation、target 生成稳定边 ID。"""
    return f"edge_{short_hash(f'{source}:{relation}:{target}')}"


class GraphService:
    """封装 graph.json 的读写和基础查询。"""

    def load_graph(self) -> GraphData:
        """从分文件存储读取图谱并组装为 GraphData。"""
        meta = read_json(GRAPH_META_FILE, {"graph_id": "ocean_kg_demo_v1", "version": 1})
        nodes_raw = read_json(GRAPH_NODES_FILE, [])
        edges_raw = read_json(GRAPH_EDGES_FILE, [])
        return GraphData(
            graph_id=meta.get("graph_id", "ocean_kg_demo_v1"),
            version=meta.get("version", 1),
            nodes=[GraphNode.model_validate(n) for n in nodes_raw],
            edges=[GraphEdge.model_validate(e) for e in edges_raw],
        )

    def save_graph(self, graph: GraphData) -> None:
        """将图谱分文件写入 meta.json、nodes.json、edges.json。"""
        write_json(GRAPH_META_FILE, {"graph_id": graph.graph_id, "version": graph.version})
        write_json(GRAPH_NODES_FILE, [n.model_dump(mode="json") for n in graph.nodes])
        write_json(GRAPH_EDGES_FILE, [e.model_dump(mode="json") for e in graph.edges])

    def get_graph(self) -> GraphData:
        """返回完整图谱。"""
        return self.load_graph()

    def get_node(self, node_id: str) -> GraphNode:
        """按节点 ID 查询节点，不存在则抛业务异常。"""
        graph = self.load_graph()

        # 当前图谱规模较小，直接线性扫描即可；后续数据增大再考虑内存索引。
        for node in graph.nodes:
            if node.id == node_id:
                return node
        raise NotFoundError(f"Node not found: {node_id}", code="NODE_NOT_FOUND")

    def get_edge(self, edge_id: str) -> GraphEdge:
        """按边 ID 查询边，不存在则抛业务异常。"""
        graph = self.load_graph()

        # 边数量目前也较小，线性扫描比维护额外索引更简单。
        for edge in graph.edges:
            if edge.id == edge_id:
                return edge
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

        去重规则：source、target、relation 三者相同即视为同一条边。
        """
        existing = self.find_edge(graph, edge.source, edge.target, edge.relation)
        if existing:
            # 已存在的边直接复用，避免重复关系污染图谱。
            return existing

        # 只有真正新增边时才提升 graph.version。
        graph.edges.append(edge)
        graph.version += 1
        return edge

    def find_similar_node(self, graph: GraphData, node_type: str, name: str) -> GraphNode | None:
        """按节点去重规则查找已有节点。"""
        for node in graph.nodes:
            if node.type == node_type and node.name == name:
                return node
        return None

    def find_edge(
        self,
        graph: GraphData,
        source: str,
        target: str,
        relation: str,
    ) -> GraphEdge | None:
        """按边去重规则查找已有边。"""
        for edge in graph.edges:
            if edge.source == source and edge.target == target and edge.relation == relation:
                return edge
        return None

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
            # 边 ID 由三元组生成，配合 add_edge 的去重规则保持稳定。
            id=generate_edge_id(source, relation, target),
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
