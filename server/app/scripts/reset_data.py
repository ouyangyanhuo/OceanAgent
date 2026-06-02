from app.core.json_store import write_json
from app.core.paths import AGENT_CACHE_FILE, AI_CACHE_FILE, EXPANSION_INDEX_FILE, REPORT_CACHE_FILE


def main() -> None:
    write_json(EXPANSION_INDEX_FILE, {})
    write_json(AI_CACHE_FILE, {})
    write_json(REPORT_CACHE_FILE, {})
    write_json(AGENT_CACHE_FILE, {})
    print("runtime indexes and caches cleared")


if __name__ == "__main__":
    main()
