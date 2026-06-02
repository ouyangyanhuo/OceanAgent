import hashlib
import re
from datetime import datetime
from typing import Any

from app.core.errors import NotFoundError
from app.core.json_store import read_json, write_json
from app.core.paths import GRAPH_FILE
from app.models.graph import GraphData, GraphEdge, GraphMetadata, GraphNode


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def to_snake_case(text: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def short_hash(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()[:8]


def generate_node_id(node_type: str, name: str, parent_node_id: str | None = None) -> str:
    prefix = to_snake_case(node_type)
    raw = f"{node_type}:{name}:{parent_node_id or ''}"
    return f"{prefix}_{short_hash(raw)}"


def generate_edge_id(source: str, relation: str, target: str) -> str:
    return f"edge_{short_hash(f'{source}:{relation}:{target}')}"


class GraphService:
    def load_graph(self) -> GraphData:
        return GraphData.model_validate(read_json(GRAPH_FILE, {"graph_id": "ocean_kg_demo_v1"}))

    def save_graph(self, graph: GraphData) -> None:
        write_json(GRAPH_FILE, graph.model_dump(mode="json"))

    def get_graph(self) -> GraphData:
        return self.load_graph()

    def get_node(self, node_id: str) -> GraphNode:
        graph = self.load_graph()
        for node in graph.nodes:
            if node.id == node_id:
                return node
        raise NotFoundError(f"Node not found: {node_id}", code="NODE_NOT_FOUND")

    def get_edge(self, edge_id: str) -> GraphEdge:
        graph = self.load_graph()
        for edge in graph.edges:
            if edge.id == edge_id:
                return edge
        raise NotFoundError(f"Edge not found: {edge_id}", code="EDGE_NOT_FOUND")

    def get_neighbors(self, node_id: str, depth: int = 1) -> dict[str, Any]:
        graph = self.load_graph()
        if not any(node.id == node_id for node in graph.nodes):
            raise NotFoundError(f"Node not found: {node_id}", code="NODE_NOT_FOUND")

        depth = max(1, min(depth, 3))
        node_by_id = {node.id: node for node in graph.nodes}
        visited = {node_id}
        frontier = {node_id}
        neighbor_edges: list[GraphEdge] = []

        for _ in range(depth):
            next_frontier: set[str] = set()
            for edge in graph.edges:
                if edge.source in frontier or edge.target in frontier:
                    neighbor_edges.append(edge)
                    other = edge.target if edge.source in frontier else edge.source
                    if other not in visited:
                        next_frontier.add(other)
                        visited.add(other)
            frontier = next_frontier

        neighbor_nodes = [node_by_id[node_id] for node_id in visited if node_id in node_by_id]
        return {"nodes": neighbor_nodes, "edges": neighbor_edges}

    def add_node(self, graph: GraphData, node: GraphNode) -> GraphNode:
        existing = self.find_similar_node(graph, node.type, node.name)
        if existing:
            return existing
        graph.nodes.append(node)
        graph.version += 1
        return node

    def add_edge(self, graph: GraphData, edge: GraphEdge) -> GraphEdge:
        existing = self.find_edge(graph, edge.source, edge.target, edge.relation)
        if existing:
            return existing
        graph.edges.append(edge)
        graph.version += 1
        return edge

    def find_similar_node(self, graph: GraphData, node_type: str, name: str) -> GraphNode | None:
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
        for edge in graph.edges:
            if edge.source == source and edge.target == target and edge.relation == relation:
                return edge
        return None

    def edge_exists(self, graph: GraphData, source: str, target: str, relation: str) -> bool:
        return self.find_edge(graph, source, target, relation) is not None

    def mark_expanded(self, graph: GraphData, node_id: str, expand_type: str) -> None:
        for node in graph.nodes:
            if node.id == node_id:
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
        created_at = now_iso()
        return GraphNode(
            id=generate_node_id(node_type, name, parent_node_id),
            type=node_type,
            name=name,
            properties=properties,
            metadata=GraphMetadata(
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
        created_at = now_iso()
        return GraphEdge(
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
