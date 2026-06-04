"""FastAPI 应用入口。

这个文件只负责装配应用：加载配置、注册中间件、注册路由、注册异常处理器，
以及在启动时确保必要的数据文件存在。业务逻辑应放在 services 层。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router, root_router
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.json_store import ensure_json_file
from app.core.paths import (
    AGENT_CACHE_FILE,
    AI_CACHE_FILE,
    EXPANSION_INDEX_FILE,
    GRAPH_EDGES_FILE,
    GRAPH_META_FILE,
    GRAPH_NODES_FILE,
    REPORT_CACHE_FILE,
    SCHEMA_RULES_FILE,
    ensure_data_dirs,
)
from app.core.response import app_error_handler

settings = get_settings()

# 创建 FastAPI 应用实例。版本号来自统一配置，便于后续健康检查和 OpenAPI 展示保持一致。
app = FastAPI(title="Ocean Agent Intelligence Platform", version=settings.version)

# CORS 只允许配置中的前端来源访问，开发环境默认支持 Vite 的 localhost/127.0.0.1。
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 业务异常统一转换为标准 API 响应，避免路由层重复 try/except。
app.add_exception_handler(AppError, app_error_handler)

# root_router 提供 /health，api_router 提供 /api/* 业务接口。
app.include_router(root_router)
app.include_router(api_router)


@app.on_event("startup")
def ensure_runtime_files() -> None:
    """启动时创建运行所需目录和 JSON 文件。

    第一版后端不使用数据库，所有状态都存到 JSON 文件。
    因此服务启动时必须保证 graph、schema、cache 等文件存在，
    这样后续 service 可以直接读取，不需要在每个业务入口重复兜底。
    """
    # 先创建目录，再创建文件；否则 ensure_json_file 写入时父目录可能不存在。
    ensure_data_dirs()

    # 图谱分文件存储：meta.json 存元信息，nodes.json 存节点，edges.json 存边。
    ensure_json_file(GRAPH_META_FILE, {"graph_id": "ocean_kg_demo_v1", "version": 1})
    ensure_json_file(GRAPH_NODES_FILE, [])
    ensure_json_file(GRAPH_EDGES_FILE, [])

    # expansion_index 记录结构扩展历史，空对象表示尚未扩展任何节点。
    ensure_json_file(EXPANSION_INDEX_FILE, {})

    # schema_rules 缺失时使用空规则兜底；真实规则由 app/data/graph/schema_rules.json 提供。
    ensure_json_file(SCHEMA_RULES_FILE, {"allowed_node_types": [], "allowed_relations": [], "expand_types": {}})

    # 三类缓存都是表达层缓存，启动时只确保文件存在，不清空已有内容。
    ensure_json_file(AI_CACHE_FILE, {})
    ensure_json_file(REPORT_CACHE_FILE, {})
    ensure_json_file(AGENT_CACHE_FILE, {})
