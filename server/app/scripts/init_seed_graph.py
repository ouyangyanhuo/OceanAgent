"""初始化种子图谱脚本。

用法：
    python -m app.scripts.init_seed_graph
    python -m app.scripts.init_seed_graph --force

当前脚本只负责创建最小 graph.json；--llm 参数预留给后续 LLM 种子生成。
"""

import argparse

from app.core.json_store import read_json, write_json
from app.core.paths import GRAPH_FILE


# 最小图谱结构，保证 GraphData 可以成功解析。
DEFAULT_GRAPH = {
    "graph_id": "ocean_kg_demo_v1",
    "version": 1,
    "nodes": [],
    "edges": [],
}


def main() -> None:
    """脚本入口。"""
    parser = argparse.ArgumentParser(description="Initialize seed graph JSON file.")
    parser.add_argument("--force", action="store_true", help="Overwrite graph.json")
    parser.add_argument("--llm", action="store_true", help="Reserved for future LLM seed generation")
    args = parser.parse_args()

    # 默认不覆盖已有 graph.json，避免误删用户已经扩展出的图谱结构。
    if GRAPH_FILE.exists() and not args.force:
        graph = read_json(GRAPH_FILE, DEFAULT_GRAPH)
        print(f"graph.json already exists: {len(graph.get('nodes', []))} nodes")
        return

    # --force 时重写为最小图谱。
    write_json(GRAPH_FILE, DEFAULT_GRAPH)
    print("graph.json initialized")


if __name__ == "__main__":
    main()
