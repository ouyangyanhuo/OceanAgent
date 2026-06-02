"""API 路由注册中心。

所有 /api/* 路由都在这里集中挂载，根路径健康检查单独放在 root_router。
"""

from fastapi import APIRouter

from app.api.routes import agent, cache, dashboard, graph, health, mock_data, report
from app.core.config import get_settings

# 业务 API 统一使用配置中的前缀，默认是 /api。
api_router = APIRouter(prefix=get_settings().api_prefix)

# 各模块路由保持扁平注册，避免 main.py 了解具体业务模块。
api_router.include_router(dashboard.router)
api_router.include_router(graph.router)
api_router.include_router(agent.router)
api_router.include_router(report.router)
api_router.include_router(mock_data.router)
api_router.include_router(cache.router)
api_router.include_router(health.api_router)

# 根路由只放无需 /api 前缀的接口，例如 /health。
root_router = APIRouter()
root_router.include_router(health.root_router)
