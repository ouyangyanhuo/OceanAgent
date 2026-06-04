"""重置运行态数据脚本。

用法：
    python -m app.scripts.reset_data              # 清空扩展索引和缓存（保留 graph.json）
    python -m app.scripts.reset_data --all         # 清空全部，包括 graph.json
"""

import argparse

from app.core.json_store import write_json
from app.core.paths import (
    AGENT_CACHE_FILE,
    AI_CACHE_FILE,
    EXPANSION_INDEX_FILE,
    GRAPH_EDGES_FILE,
    GRAPH_META_FILE,
    GRAPH_NODES_FILE,
    REPORT_CACHE_FILE,
)


def main() -> None:
    """清空扩展索引和缓存文件。"""
    parser = argparse.ArgumentParser(description="Reset runtime data files.")
    parser.add_argument("--all", action="store_true", help="Also clear graph.json")
    args = parser.parse_args()

    write_json(EXPANSION_INDEX_FILE, {})
    write_json(AI_CACHE_FILE, {})
    write_json(REPORT_CACHE_FILE, {})
    write_json(AGENT_CACHE_FILE, {})
    print("✓ expansion_index.json cleared")
    print("✓ cache files cleared")

    if args.all:
        write_json(GRAPH_META_FILE, {"graph_id": "ocean_kg_demo_v1", "version": 1})
        write_json(GRAPH_NODES_FILE, [])
        write_json(GRAPH_EDGES_FILE, [])
        print("✓ graph files cleared (meta.json, nodes.json, edges.json)")

    print("\n重置完成。重启后端后生效。")
    if not args.all:
        print("提示: 使用 --all 可同时清空 graph.json 中的节点和边。")


if __name__ == "__main__":
    main()
