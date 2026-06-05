"""节点扩展服务。

扩展流程是图谱结构变化的主入口：
1. 检查节点和 expand_type
2. 命中 expansion_index 时直接复用旧结果
3. 构造上下文并调用 AIService 生成候选数据
4. 校验候选数据
5. 后端生成 ID、去重、写入 graph.json
6. 更新 expansion_index 并创建快照
"""

from typing import Any

from app.core.json_store import read_json, write_json
from app.core.paths import EXPANSION_INDEX_FILE
from app.models.graph import ExpandNodeResponse, GraphData, GraphEdge, GraphNode
from app.services.ai_service import AIService
from app.services.graph_service import GraphService, now_iso
from app.services.notification_service import NotificationService
from app.services.snapshot_service import SnapshotService
from app.services.validation_service import ValidationService


class ExpansionService:
    """编排节点扩展完整流程。"""

    def __init__(self) -> None:
        """初始化依赖服务。"""
        self.graph_service = GraphService()
        self.ai_service = AIService()
        self.validation_service = ValidationService()
        self.snapshot_service = SnapshotService()
        self.notification_service = NotificationService()

    def expand_node(
        self,
        node_id: str,
        expand_type: str,
        force_refresh: bool = False,
    ) -> ExpandNodeResponse:
        """扩展指定节点。

        force_refresh=False 时，同一 node_id + expand_type 如果已扩展过，
        会直接从 expansion_index 读取历史结果，保证结构层稳定。
        """
        # 先加载当前图谱快照。后续会重新加载一次写入，是为了让读阶段和写阶段职责分开。
        graph = self.graph_service.load_graph()

        # 确认中心节点存在；不存在时 _find_node 会抛 NODE_NOT_FOUND。
        center_node = self._find_node(graph, node_id)

        # 提前校验 expand_type，避免无效扩展进入 AI/mock 生成阶段。
        self.validation_service.get_expand_rule(expand_type)

        # 图谱结构扩展不使用概率缓存，只要索引存在就稳定复用。
        if not force_refresh:
            existing = self.get_existing_expansion(node_id, expand_type)
            if existing:
                return existing

        # LLM 只返回候选结构，真正写入前必须经过后端校验。
        context = self.build_expansion_context(node_id, expand_type)

        # 当前 AIService 返回 mock 数据；未来真实 LLM 也应返回同样的候选结构。
        llm_result = self.ai_service.generate_graph_expansion(context)

        # 校验只确认候选数据合法，不负责生成 ID 或写入 graph.json。
        valid_result = self.validation_service.validate_expansion_result(llm_result, expand_type, graph)

        # apply_expansion_result 会重新加载图谱、正式构造节点/边并落盘。
        response = self.apply_expansion_result(node_id, expand_type, valid_result)

        # 保证响应能立即体现本次扩展结果，不依赖调用方再次请求节点详情。
        response.center_node.expanded[expand_type] = True
        return response

    def get_existing_expansion(
        self,
        node_id: str,
        expand_type: str,
    ) -> ExpandNodeResponse | None:
        """从 expansion_index.json 读取已有扩展结果。"""
        index = read_json(EXPANSION_INDEX_FILE, {})

        # expansion_index 的 key 固定为 node_id:expand_type，表示某个节点某种扩展已做过。
        item = index.get(self._index_key(node_id, expand_type))
        if not item:
            return None

        # 命中索引后仍读取 graph.json，是因为索引只记录结果 ID，不保存完整对象。
        graph = self.graph_service.load_graph()
        center_node = self._find_node(graph, node_id)

        # 转成 set 是为了后面 O(1) 判断节点/边是否属于本次历史扩展结果。
        node_ids = set(item.get("generated_node_ids", []))
        edge_ids = set(item.get("generated_edge_ids", []))
        # 索引只保存 ID，返回时从当前 graph.json 反查完整节点和边。
        return ExpandNodeResponse(
            center_node=center_node,
            new_nodes=[node for node in graph.nodes if node.id in node_ids],
            new_edges=[edge for edge in graph.edges if edge.id in edge_ids],
            from_cache=True,
            summary=item.get("summary"),
        )

    def build_expansion_context(self, node_id: str, expand_type: str) -> dict[str, Any]:
        """构造图谱扩展上下文。

        上下文包含中心节点、一跳邻居、已有边、扩展规则等信息，
        后续可直接用于 prompt 渲染或真实 LLM 请求。
        """
        graph = self.graph_service.load_graph()
        center_node = self._find_node(graph, node_id)

        # 扩展时只取一跳邻居，避免 prompt 上下文太大，也符合第一版轻量设计。
        neighbors = self.graph_service.get_neighbors(node_id, depth=1)

        # schema_rules 中限定了此 expand_type 允许生成的节点类型、关系类型和数量上限。
        rule = self.validation_service.get_expand_rule(expand_type)
        return {
            # 当前节点是扩展中心，LLM/mock 需要围绕它生成候选结构。
            "current_node": center_node.model_dump(mode="json"),
            # 邻居帮助生成结果避开已有关系，也给分析提供局部图谱上下文。
            "neighbors": {
                "nodes": [node.model_dump(mode="json") for node in neighbors["nodes"]],
                "edges": [edge.model_dump(mode="json") for edge in neighbors["edges"]],
            },
            # 提供全部已有边，后续 prompt 或真实 LLM 可以避免重复关系。
            "existing_edges": [edge.model_dump(mode="json") for edge in graph.edges],
            "expand_type": expand_type,
            "allowed_node_types": rule["allowed_node_types"],
            "allowed_relations": rule["allowed_relations"],
            "max_nodes": rule["max_nodes"],
            "max_edges": rule["max_edges"],
        }

    def apply_expansion_result(
        self,
        node_id: str,
        expand_type: str,
        llm_result: dict[str, Any],
    ) -> ExpandNodeResponse:
        """把校验后的候选扩展结果写入图谱。"""
        def mutate(graph: GraphData) -> dict[str, Any]:
            center_node = self._find_node(graph, node_id)
            if center_node.expanded.get(expand_type):
                return {"skipped_existing": True, "center_node": center_node, "nodes": [], "edges": []}

            # 这两个列表用于构造响应和写 expansion_index。
            generated_nodes: list[GraphNode] = []
            generated_edges: list[GraphEdge] = []

            # LLM 候选边常用中文 name 引用节点；这里先建立已有节点 name -> id 映射。
            node_ref_by_name = {node.name: node.id for node in graph.nodes}

            # 同时允许候选边直接使用中心节点 ID。
            node_ref_by_name[center_node.id] = center_node.id

            # 先写节点，再建立 name/id 到正式节点 ID 的映射，供边引用解析。
            for candidate in llm_result.get("nodes", []):
                # build_node 统一补齐 ID 和 metadata，避免信任 LLM 生成的 ID。
                node = self.graph_service.build_node(
                    candidate["type"],
                    candidate["name"],
                    candidate.get("properties", {}),
                    parent_node_id=node_id,
                )

                # add_node 内部会按 type+name 去重；stored 可能是已有节点，也可能是新节点。
                stored = self.graph_service.add_node(graph, node)

                # 将正式存储节点加入映射，使后续边可以通过 name 或 id 找到正确 target。
                node_ref_by_name[stored.name] = stored.id
                node_ref_by_name[stored.id] = stored.id
                generated_nodes.append(stored)

            # 候选边可以用 source_ref/target_name 指向中心节点或本次生成节点。
            for candidate in llm_result.get("edges", []):
                # source_ref 缺省时默认从中心节点出发，适配简单扩展结果。
                source_ref = candidate.get("source_ref", node_id)

                # target_ref 兼容未来可能直接提供 target_ref 的结构；当前 mock 使用 target_name。
                target_ref = candidate.get("target_ref") or candidate.get("target_name")

                # 如果 ref 是中文 name，则映射到正式节点 ID；如果已经是 ID，则保持原值。
                source = node_ref_by_name.get(source_ref, source_ref)
                target = node_ref_by_name.get(target_ref, target_ref)

                # build_edge 统一生成 edge ID 和 metadata。
                edge = self.graph_service.build_edge(
                    source=source,
                    target=target,
                    relation=candidate["relation"],
                    weight=float(candidate.get("weight", 1.0)),
                    properties=candidate.get("properties", {}),
                    parent_node_id=node_id,
                )

                # add_edge 内部会按 source+target+relation+业务键 去重。
                stored_edge = self.graph_service.add_edge(graph, edge)
                generated_edges.append(stored_edge)

            # 结构性变化统一落盘：graph、扩展索引、快照三者一起更新。
            self.graph_service.mark_expanded(graph, node_id, expand_type)
            return {
                "skipped_existing": False,
                "center_node": self._find_node(graph, node_id),
                "nodes": generated_nodes,
                "edges": generated_edges,
            }

        mutation, graph = self.graph_service.apply_mutation(
            reason=f"expand:{node_id}:{expand_type}",
            mutator=mutate,
        )

        if mutation["skipped_existing"]:
            existing = self.get_existing_expansion(node_id, expand_type)
            if existing:
                return existing
            return ExpandNodeResponse(center_node=mutation["center_node"], from_cache=True, summary=llm_result.get("summary"))

        generated_nodes = mutation["nodes"]
        generated_edges = mutation["edges"]
        center_node = mutation["center_node"]

        # 索引必须在 graph 写入后更新，保证索引中的 ID 能在 graph.json 中找到。
        self._write_index(
            node_id=node_id,
            expand_type=expand_type,
            nodes=generated_nodes,
            edges=generated_edges,
            summary=llm_result.get("summary"),
        )

        # 创建快照放在最后；快照记录的是本次扩展完成后的图谱版本。
        self.snapshot_service.create_snapshot(graph, reason=f"expand:{node_id}:{expand_type}")

        # 推送通知：图谱扩展完成
        node_count = len(generated_nodes)
        edge_count = len(generated_edges)
        self.notification_service.create_notification(
            title="图谱扩展完成",
            message=f"节点「{center_node.name}」的 {expand_type} 扩展已完成，新增 {node_count} 个节点和 {edge_count} 条边",
            notification_type="graph_expansion",
            related_node_id=node_id,
        )

        return ExpandNodeResponse(
            center_node=center_node,
            new_nodes=generated_nodes,
            new_edges=generated_edges,
            from_cache=False,
            summary=llm_result.get("summary"),
        )

    def _write_index(
        self,
        node_id: str,
        expand_type: str,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
        summary: str | None,
    ) -> None:
        """写入 expansion_index.json。

        索引用 node_id:expand_type 作为 key，记录本次扩展生成的节点和边 ID。
        """
        index = read_json(EXPANSION_INDEX_FILE, {})
        timestamp = now_iso()
        key = self._index_key(node_id, expand_type)

        # created_at 首次扩展时写入；force_refresh 后保留原 created_at，只更新 updated_at。
        index[key] = {
            "node_id": node_id,
            "expand_type": expand_type,
            "expanded": True,
            "generated_node_ids": [node.id for node in nodes],
            "generated_edge_ids": [edge.id for edge in edges],
            "summary": summary,
            "created_at": index.get(key, {}).get("created_at", timestamp),
            "updated_at": timestamp,
        }

        # expansion_index 是结构稳定性的关键文件，写入也走 json_store 的文件锁和原子写。
        write_json(EXPANSION_INDEX_FILE, index)

    def _find_node(self, graph: GraphData, node_id: str) -> GraphNode:
        """在已加载图谱中查找节点，找不到时复用 GraphService 的标准异常。"""
        for node in graph.nodes:
            if node.id == node_id:
                return node
        return self.graph_service.get_node(node_id)

    def _index_key(self, node_id: str, expand_type: str) -> str:
        """生成扩展索引 key。"""
        return f"{node_id}:{expand_type}"
