"""初始化种子图谱脚本。

用法：
    python -m app.scripts.init_seed_graph              # 创建空图谱（已存在则跳过）
    python -m app.scripts.init_seed_graph --force       # 强制重写为空图谱
    python -m app.scripts.init_seed_graph --llm         # 清空后用 LLM 生成种子图谱
    python -m app.scripts.init_seed_graph --force --llm # 同上
"""

import argparse
import sys

from app.core.config import get_settings
from app.core.json_store import read_json, write_json
from app.core.paths import (
    EXPANSION_INDEX_FILE,
    GRAPH_EDGES_FILE,
    GRAPH_META_FILE,
    GRAPH_NODES_FILE,
)


def _empty_graph_files() -> None:
    """将图谱三个文件清空为初始状态。"""
    write_json(GRAPH_META_FILE, {"graph_id": "ocean_kg_demo_v1", "version": 1})
    write_json(GRAPH_NODES_FILE, [])
    write_json(GRAPH_EDGES_FILE, [])


def main() -> None:
    """脚本入口。"""
    parser = argparse.ArgumentParser(description="Initialize seed graph JSON file.")
    parser.add_argument("--force", action="store_true", help="Overwrite graph.json")
    parser.add_argument("--llm", action="store_true", help="Use LLM to generate seed graph")
    args = parser.parse_args()

    # 默认不覆盖已有图谱文件，避免误删用户已经扩展出的图谱结构。
    # 但 0 节点视为空图谱，允许重新生成。
    nodes = read_json(GRAPH_NODES_FILE, [])
    if len(nodes) > 0 and not args.force and not args.llm:
        print(f"graph already exists: {len(nodes)} nodes")
        return

    if args.llm:
        _generate_llm_seed()
    else:
        _empty_graph_files()
        print("graph initialized (empty)")


def _generate_llm_seed() -> None:
    """使用 LLM 生成种子图谱。"""
    settings = get_settings()

    if settings.use_mock_llm:
        print("错误: 使用 --llm 需要配置 LLM_API_KEY 环境变量", file=sys.stderr)
        print("请在 .env 或环境变量中设置:", file=sys.stderr)
        print("  LLM_PROVIDER=openai", file=sys.stderr)
        print("  LLM_API_KEY=sk-xxx", file=sys.stderr)
        print("  LLM_BASE_URL=https://api.openai.com/v1", file=sys.stderr)
        print("  LLM_MODEL=gpt-4o-mini", file=sys.stderr)
        sys.exit(1)

    # 延迟导入，避免无 LLM 时也加载 httpx
    from app.services.ai_service import AIService
    from app.services.expansion_service import ExpansionService
    from app.services.graph_service import GraphService

    print(f"正在使用 LLM ({settings.llm_model}) 生成种子图谱...")

    # 1. 清空图谱和扩展索引
    _empty_graph_files()
    write_json(EXPANSION_INDEX_FILE, {})
    print("  已清空图谱文件和 expansion_index.json")

    # 2. 用 LLM 生成种子候选数据
    ai_service = AIService()
    graph_service = GraphService()
    expansion_service = ExpansionService()

    seed_result = ai_service.generate_graph_seed("中国近海海域")
    print(f"  LLM 返回 {len(seed_result.get('nodes', []))} 个候选节点, {len(seed_result.get('edges', []))} 条候选边")

    # 3. 将候选节点写入图谱
    graph = graph_service.load_graph()
    node_ref_by_name = {}

    for candidate in seed_result.get("nodes", []):
        node = graph_service.build_node(
            candidate["type"],
            candidate["name"],
            candidate.get("properties", {}),
            source="seed",
        )
        stored = graph_service.add_node(graph, node)
        node_ref_by_name[stored.name] = stored.id
        node_ref_by_name[stored.id] = stored.id
        print(f"  + 节点: {stored.name} ({stored.type})")

    # 4. 将候选边写入图谱（跳过引用不存在节点的边）
    for candidate in seed_result.get("edges", []):
        source_ref = candidate.get("source_ref", "")
        target_ref = candidate.get("target_ref") or candidate.get("target_name", "")
        source = node_ref_by_name.get(source_ref, source_ref)
        target = node_ref_by_name.get(target_ref, target_ref)

        # 检查引用的节点是否存在，跳过悬挂边
        existing_ids = {node.id for node in graph.nodes}
        if source not in existing_ids:
            print(f"  ⚠ 跳过边: source '{source_ref}' 解析为 '{source}' 但节点不存在")
            continue
        if target not in existing_ids:
            print(f"  ⚠ 跳过边: target '{target_ref}' 解析为 '{target}' 但节点不存在")
            continue

        edge = graph_service.build_edge(
            source=source,
            target=target,
            relation=candidate["relation"],
            weight=float(candidate.get("weight", 1.0)),
            properties=candidate.get("properties", {}),
            source_name="seed",
        )
        stored_edge = graph_service.add_edge(graph, edge)
        print(f"  + 边: {stored_edge.source} --[{stored_edge.relation}]--> {stored_edge.target}")

    graph_service.save_graph(graph)
    summary = seed_result.get("summary", "")
    print(f"\n种子图谱生成完成: {len(graph.nodes)} 个节点, {len(graph.edges)} 条边")
    if summary:
        print(f"摘要: {summary}")


if __name__ == "__main__":
    main()
