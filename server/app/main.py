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
    GRAPH_FILE,
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
    ensure_data_dirs()
    ensure_json_file(GRAPH_FILE, {"graph_id": "ocean_kg_demo_v1", "version": 1, "nodes": [], "edges": []})
    ensure_json_file(EXPANSION_INDEX_FILE, {})
    ensure_json_file(SCHEMA_RULES_FILE, {"allowed_node_types": [], "allowed_relations": [], "expand_types": {}})
    ensure_json_file(AI_CACHE_FILE, {})
    ensure_json_file(REPORT_CACHE_FILE, {})
    ensure_json_file(AGENT_CACHE_FILE, {})
