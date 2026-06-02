"""重置运行态索引和缓存脚本。

该脚本不会清空 graph.json，只清空 expansion_index 和表达层缓存。
"""

from app.core.json_store import write_json
from app.core.paths import AGENT_CACHE_FILE, AI_CACHE_FILE, EXPANSION_INDEX_FILE, REPORT_CACHE_FILE


def main() -> None:
    """清空扩展索引和缓存文件。"""
    write_json(EXPANSION_INDEX_FILE, {})
    write_json(AI_CACHE_FILE, {})
    write_json(REPORT_CACHE_FILE, {})
    write_json(AGENT_CACHE_FILE, {})
    print("runtime indexes and caches cleared")


if __name__ == "__main__":
    main()
