"""图谱文件校验脚本。

当前校验重点是 graph.json 能被模型解析，并且所有边都指向存在的节点。
"""

from app.services.graph_service import GraphService


def main() -> None:
    """执行图谱一致性校验。"""
    graph = GraphService().get_graph()
    node_ids = {node.id for node in graph.nodes}

    # 找出 source 或 target 不存在的悬挂边。
    dangling_edges = [
        edge.id
        for edge in graph.edges
        if edge.source not in node_ids or edge.target not in node_ids
    ]
    if dangling_edges:
        # 用非 0 退出码让 CI 或脚本调用方能识别失败。
        raise SystemExit(f"Dangling edges: {', '.join(dangling_edges)}")
    print(f"graph valid: {len(graph.nodes)} nodes, {len(graph.edges)} edges")


if __name__ == "__main__":
    main()
