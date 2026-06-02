from app.services.graph_service import GraphService


def main() -> None:
    graph = GraphService().get_graph()
    node_ids = {node.id for node in graph.nodes}
    dangling_edges = [
        edge.id
        for edge in graph.edges
        if edge.source not in node_ids or edge.target not in node_ids
    ]
    if dangling_edges:
        raise SystemExit(f"Dangling edges: {', '.join(dangling_edges)}")
    print(f"graph valid: {len(graph.nodes)} nodes, {len(graph.edges)} edges")


if __name__ == "__main__":
    main()
