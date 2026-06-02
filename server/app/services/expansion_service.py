from typing import Any

from app.core.json_store import read_json, write_json
from app.core.paths import EXPANSION_INDEX_FILE
from app.models.graph import ExpandNodeResponse, GraphData, GraphEdge, GraphNode
from app.services.ai_service import AIService
from app.services.graph_service import GraphService, now_iso
from app.services.snapshot_service import SnapshotService
from app.services.validation_service import ValidationService


class ExpansionService:
    def __init__(self) -> None:
        self.graph_service = GraphService()
        self.ai_service = AIService()
        self.validation_service = ValidationService()
        self.snapshot_service = SnapshotService()

    def expand_node(
        self,
        node_id: str,
        expand_type: str,
        force_refresh: bool = False,
    ) -> ExpandNodeResponse:
        graph = self.graph_service.load_graph()
        center_node = self._find_node(graph, node_id)
        self.validation_service.get_expand_rule(expand_type)

        if not force_refresh:
            existing = self.get_existing_expansion(node_id, expand_type)
            if existing:
                return existing

        context = self.build_expansion_context(node_id, expand_type)
        llm_result = self.ai_service.generate_graph_expansion(context)
        valid_result = self.validation_service.validate_expansion_result(llm_result, expand_type, graph)
        response = self.apply_expansion_result(node_id, expand_type, valid_result)
        response.center_node = center_node.model_copy(update={"expanded": {**center_node.expanded, expand_type: True}})
        return response

    def get_existing_expansion(
        self,
        node_id: str,
        expand_type: str,
    ) -> ExpandNodeResponse | None:
        index = read_json(EXPANSION_INDEX_FILE, {})
        item = index.get(self._index_key(node_id, expand_type))
        if not item:
            return None
        graph = self.graph_service.load_graph()
        center_node = self._find_node(graph, node_id)
        node_ids = set(item.get("generated_node_ids", []))
        edge_ids = set(item.get("generated_edge_ids", []))
        return ExpandNodeResponse(
            center_node=center_node,
            new_nodes=[node for node in graph.nodes if node.id in node_ids],
            new_edges=[edge for edge in graph.edges if edge.id in edge_ids],
            from_cache=True,
            summary=item.get("summary"),
        )

    def build_expansion_context(self, node_id: str, expand_type: str) -> dict[str, Any]:
        graph = self.graph_service.load_graph()
        center_node = self._find_node(graph, node_id)
        neighbors = self.graph_service.get_neighbors(node_id, depth=1)
        rule = self.validation_service.get_expand_rule(expand_type)
        return {
            "current_node": center_node.model_dump(mode="json"),
            "neighbors": {
                "nodes": [node.model_dump(mode="json") for node in neighbors["nodes"]],
                "edges": [edge.model_dump(mode="json") for edge in neighbors["edges"]],
            },
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
        graph = self.graph_service.load_graph()
        center_node = self._find_node(graph, node_id)
        generated_nodes: list[GraphNode] = []
        generated_edges: list[GraphEdge] = []
        node_ref_by_name = {node.name: node.id for node in graph.nodes}
        node_ref_by_name[center_node.id] = center_node.id

        for candidate in llm_result.get("nodes", []):
            node = self.graph_service.build_node(
                candidate["type"],
                candidate["name"],
                candidate.get("properties", {}),
                parent_node_id=node_id,
            )
            stored = self.graph_service.add_node(graph, node)
            node_ref_by_name[stored.name] = stored.id
            node_ref_by_name[stored.id] = stored.id
            generated_nodes.append(stored)

        for candidate in llm_result.get("edges", []):
            source_ref = candidate.get("source_ref", node_id)
            target_ref = candidate.get("target_ref") or candidate.get("target_name")
            source = node_ref_by_name.get(source_ref, source_ref)
            target = node_ref_by_name.get(target_ref, target_ref)
            edge = self.graph_service.build_edge(
                source=source,
                target=target,
                relation=candidate["relation"],
                weight=float(candidate.get("weight", 1.0)),
                properties=candidate.get("properties", {}),
                parent_node_id=node_id,
            )
            stored_edge = self.graph_service.add_edge(graph, edge)
            generated_edges.append(stored_edge)

        self.graph_service.mark_expanded(graph, node_id, expand_type)
        self.graph_service.save_graph(graph)
        self._write_index(
            node_id=node_id,
            expand_type=expand_type,
            nodes=generated_nodes,
            edges=generated_edges,
            summary=llm_result.get("summary"),
        )
        self.snapshot_service.create_snapshot(graph, reason=f"expand:{node_id}:{expand_type}")

        return ExpandNodeResponse(
            center_node=self._find_node(graph, node_id),
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
        index = read_json(EXPANSION_INDEX_FILE, {})
        timestamp = now_iso()
        key = self._index_key(node_id, expand_type)
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
        write_json(EXPANSION_INDEX_FILE, index)

    def _find_node(self, graph: GraphData, node_id: str) -> GraphNode:
        for node in graph.nodes:
            if node.id == node_id:
                return node
        return self.graph_service.get_node(node_id)

    def _index_key(self, node_id: str, expand_type: str) -> str:
        return f"{node_id}:{expand_type}"
