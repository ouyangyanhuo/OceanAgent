from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"

GRAPH_DIR = DATA_DIR / "graph"
MOCK_DIR = DATA_DIR / "mock"
CACHE_DIR = DATA_DIR / "cache"
SNAPSHOT_DIR = DATA_DIR / "snapshots"
PROMPT_DIR = DATA_DIR / "prompts"

GRAPH_FILE = GRAPH_DIR / "graph.json"
EXPANSION_INDEX_FILE = GRAPH_DIR / "expansion_index.json"
SCHEMA_RULES_FILE = GRAPH_DIR / "schema_rules.json"

OCEAN_OBSERVATIONS_FILE = MOCK_DIR / "ocean_observations.json"
BUOY_STATUS_FILE = MOCK_DIR / "buoy_status.json"
CURRENT_FIELDS_FILE = MOCK_DIR / "current_fields.json"
FISHERY_AREAS_FILE = MOCK_DIR / "fishery_areas.json"
ROUTES_FILE = MOCK_DIR / "routes.json"

AI_CACHE_FILE = CACHE_DIR / "ai_cache.json"
REPORT_CACHE_FILE = CACHE_DIR / "report_cache.json"
AGENT_CACHE_FILE = CACHE_DIR / "agent_cache.json"


def ensure_data_dirs() -> None:
    for directory in [GRAPH_DIR, MOCK_DIR, CACHE_DIR, SNAPSHOT_DIR, PROMPT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
