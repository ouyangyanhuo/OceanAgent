"""节点操作服务。

提供新建种子节点和节点连接功能，复用图谱读写和 LLM 调用的基础设施。
"""

from typing import Any

from app.models.graph import (
    ConnectNodesResponse,
    CreateSeedNodeResponse,
    GraphData,
    GraphEdge,
    GraphNode,
)
from app.services.ai_service import AIService
from app.services.graph_service import GraphService
from app.services.notification_service import NotificationService
from app.services.snapshot_service import SnapshotService

# 全局允许的节点类型和关系类型
ALLOWED_NODE_TYPES = [
    "Buoy", "Observation", "RiskFactor", "RedTideEvent",
    "Species", "FisheryArea", "PreventionMeasure",
]
ALLOWED_RELATIONS = [
    "has_observation", "has_risk_event", "affected_by",
    "indicates", "may_trigger", "mitigated_by", "correlated_with",
]


class NodeOperationsService:
    """编排新建种子节点和节点连接流程。"""

    def __init__(self) -> None:
        self.graph_service = GraphService()
        self.ai_service = AIService()
        self.snapshot_service = SnapshotService()
        self.notification_service = NotificationService()

    def create_seed_node(self, description: str) -> CreateSeedNodeResponse:
        """根据用户描述创建种子节点及关联节点。"""
        graph = self.graph_service.load_graph()

        # 构造上下文
        context = {
            "description": description,
            "existing_nodes": [
                {"name": n.name, "type": n.type} for n in graph.nodes
            ],
            "allowed_node_types": ALLOWED_NODE_TYPES,
            "allowed_relations": ALLOWED_RELATIONS,
        }

        # 调用 LLM 生成候选数据
        llm_result = self.ai_service.generate_seed_node(context)

        # 解析结果
        seed_candidate = llm_result["seed_node"]
        extra_nodes = llm_result.get("nodes", [])
        edge_candidates = llm_result.get("edges", [])

        def mutate(graph: GraphData) -> dict[str, Any]:
            # 构建 name -> id 映射
            node_ref_by_name: dict[str, str] = {}
            generated_nodes: list[GraphNode] = []
            generated_edges: list[GraphEdge] = []

            # 1. 创建种子节点
            seed_node = self.graph_service.build_node(
                node_type=seed_candidate["type"],
                name=seed_candidate["name"],
                properties=seed_candidate.get("properties", {}),
                source="seed",
            )
            stored_seed = self.graph_service.add_node(graph, seed_node)
            node_ref_by_name["seed_node"] = stored_seed.id
            node_ref_by_name[stored_seed.name] = stored_seed.id
            node_ref_by_name[stored_seed.id] = stored_seed.id
            generated_nodes.append(stored_seed)

            # 2. 创建额外节点
            for candidate in extra_nodes:
                node = self.graph_service.build_node(
                    node_type=candidate["type"],
                    name=candidate["name"],
                    properties=candidate.get("properties", {}),
                    parent_node_id=stored_seed.id,
                )
                stored = self.graph_service.add_node(graph, node)
                node_ref_by_name[stored.name] = stored.id
                node_ref_by_name[stored.id] = stored.id
                generated_nodes.append(stored)

            # 3. 创建边
            for candidate in edge_candidates:
                source_ref = candidate.get("source_ref", "seed_node")
                target_ref = candidate.get("target_ref") or candidate.get("target_name")

                source = node_ref_by_name.get(source_ref, source_ref)
                target = node_ref_by_name.get(target_ref, target_ref)

                edge = self.graph_service.build_edge(
                    source=source,
                    target=target,
                    relation=candidate["relation"],
                    weight=float(candidate.get("weight", 1.0)),
                    properties=candidate.get("properties", {}),
                    parent_node_id=stored_seed.id,
                )
                stored_edge = self.graph_service.add_edge(graph, edge)
                generated_edges.append(stored_edge)

            return {
                "seed_node": stored_seed,
                "nodes": generated_nodes,
                "edges": generated_edges,
            }

        mutation, graph = self.graph_service.apply_mutation("create_seed", mutate)
        stored_seed = mutation["seed_node"]
        generated_nodes = mutation["nodes"]
        generated_edges = mutation["edges"]
        self.snapshot_service.create_snapshot(graph, reason=f"create_seed:{stored_seed.id}")

        # 推送通知
        self.notification_service.create_notification(
            title="种子节点创建完成",
            message=f"已创建种子节点「{stored_seed.name}」及 {len(generated_edges)} 条关联边",
            notification_type="seed_node_created",
            related_node_id=stored_seed.id,
        )

        return CreateSeedNodeResponse(
            seed_node=stored_seed,
            new_nodes=[n for n in generated_nodes if n.id != stored_seed.id],
            new_edges=generated_edges,
            summary=llm_result.get("summary"),
        )

    def connect_nodes(self, source_node_id: str, target_node_id: str) -> ConnectNodesResponse:
        """在两个节点之间建立连接，生成中间桥梁节点。"""
        graph = self.graph_service.load_graph()

        # 查找两个节点
        source_node = self._find_node(graph, source_node_id)
        target_node = self._find_node(graph, target_node_id)

        # 构造上下文
        context = {
            "source_node": source_node.model_dump(mode="json"),
            "target_node": target_node.model_dump(mode="json"),
            "allowed_node_types": ALLOWED_NODE_TYPES,
            "allowed_relations": ALLOWED_RELATIONS,
        }

        # 调用 LLM
        llm_result = self.ai_service.generate_node_connection(context)

        # 解析结果
        bridge_candidate = llm_result["bridge_node"]
        edge_candidates = llm_result.get("edges", [])

        def mutate(graph: GraphData) -> dict[str, Any]:
            current_source_node = self._find_node(graph, source_node_id)
            current_target_node = self._find_node(graph, target_node_id)
            node_ref_by_name: dict[str, str] = {
                current_source_node.name: current_source_node.id,
                current_source_node.id: current_source_node.id,
                current_target_node.name: current_target_node.id,
                current_target_node.id: current_target_node.id,
            }
            generated_edges: list[GraphEdge] = []

            # 1. 创建桥梁节点
            bridge_node = self.graph_service.build_node(
                node_type=bridge_candidate["type"],
                name=bridge_candidate["name"],
                properties=bridge_candidate.get("properties", {}),
                parent_node_id=source_node_id,
            )
            stored_bridge = self.graph_service.add_node(graph, bridge_node)
            node_ref_by_name[stored_bridge.name] = stored_bridge.id
            node_ref_by_name[stored_bridge.id] = stored_bridge.id

            # 2. 创建边
            for candidate in edge_candidates:
                source_ref = candidate.get("source_ref", "")
                target_ref = candidate.get("target_ref") or candidate.get("target_name")

                source = node_ref_by_name.get(source_ref, source_ref)
                target = node_ref_by_name.get(target_ref, target_ref)

                edge = self.graph_service.build_edge(
                    source=source,
                    target=target,
                    relation=candidate["relation"],
                    weight=float(candidate.get("weight", 1.0)),
                    properties=candidate.get("properties", {}),
                    parent_node_id=stored_bridge.id,
                )
                stored_edge = self.graph_service.add_edge(graph, edge)
                generated_edges.append(stored_edge)

            return {
                "source_node": current_source_node,
                "target_node": current_target_node,
                "bridge_node": stored_bridge,
                "edges": generated_edges,
            }

        mutation, graph = self.graph_service.apply_mutation(
            f"connect:{source_node_id}:{target_node_id}",
            mutate,
        )
        source_node = mutation["source_node"]
        target_node = mutation["target_node"]
        stored_bridge = mutation["bridge_node"]
        generated_edges = mutation["edges"]
        self.snapshot_service.create_snapshot(graph, reason=f"connect:{source_node_id}:{target_node_id}")

        # 推送通知
        self.notification_service.create_notification(
            title="节点连接完成",
            message=f"已通过桥梁节点「{stored_bridge.name}」连接「{source_node.name}」和「{target_node.name}」",
            notification_type="node_connected",
            related_node_id=stored_bridge.id,
        )

        return ConnectNodesResponse(
            source_node=source_node,
            target_node=target_node,
            bridge_node=stored_bridge,
            new_edges=generated_edges,
            summary=llm_result.get("summary"),
        )

    def _find_node(self, graph: GraphData, node_id: str) -> GraphNode:
        for node in graph.nodes:
            if node.id == node_id:
                return node
        return self.graph_service.get_node(node_id)
