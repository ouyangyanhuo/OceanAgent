"""后端文件路径集中管理。

所有 JSON 数据、缓存、快照和 Prompt 都放在 app/data 下。
服务层必须从这里导入路径，避免在各处手写相对路径。
"""

from pathlib import Path

# app 目录，即 server/app。
APP_DIR = Path(__file__).resolve().parents[1]

# 第一版后端的唯一持久化根目录。
DATA_DIR = APP_DIR / "data"

# 数据目录按用途拆分，便于后续备份、重置和文档说明。
GRAPH_DIR = DATA_DIR / "graph"
MOCK_DIR = DATA_DIR / "mock"
CACHE_DIR = DATA_DIR / "cache"
SNAPSHOT_DIR = DATA_DIR / "snapshots"
PROMPT_DIR = DATA_DIR / "prompts"

# 图谱事实源（分文件存储）和图谱扩展控制文件。
GRAPH_FILE = GRAPH_DIR / "graph.json"  # 兼容旧文件，迁移后可删除
GRAPH_META_FILE = GRAPH_DIR / "meta.json"
GRAPH_NODES_FILE = GRAPH_DIR / "nodes.json"
GRAPH_EDGES_FILE = GRAPH_DIR / "edges.json"
EXPANSION_INDEX_FILE = GRAPH_DIR / "expansion_index.json"
SCHEMA_RULES_FILE = GRAPH_DIR / "schema_rules.json"

# Mock 海洋数据文件，供 API 展示和智能体上下文使用。
OCEAN_OBSERVATIONS_FILE = MOCK_DIR / "ocean_observations.json"
BUOY_STATUS_FILE = MOCK_DIR / "buoy_status.json"
CURRENT_FIELDS_FILE = MOCK_DIR / "current_fields.json"
FISHERY_AREAS_FILE = MOCK_DIR / "fishery_areas.json"
ROUTES_FILE = MOCK_DIR / "routes.json"

# 表达层缓存文件。图谱结构扩展不使用这些概率缓存。
AI_CACHE_FILE = CACHE_DIR / "ai_cache.json"
REPORT_CACHE_FILE = CACHE_DIR / "report_cache.json"
AGENT_CACHE_FILE = CACHE_DIR / "agent_cache.json"

# 通知数据文件。
NOTIFICATION_FILE = DATA_DIR / "notifications.json"


def ensure_data_dirs() -> None:
    """确保所有数据子目录存在。

    该函数在应用启动时调用，也可被脚本复用。
    """
    for directory in [GRAPH_DIR, MOCK_DIR, CACHE_DIR, SNAPSHOT_DIR, PROMPT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
