from fastapi import APIRouter

from app.api.routes import agent, cache, dashboard, graph, health, mock_data, report
from app.core.config import get_settings

api_router = APIRouter(prefix=get_settings().api_prefix)
api_router.include_router(dashboard.router)
api_router.include_router(graph.router)
api_router.include_router(agent.router)
api_router.include_router(report.router)
api_router.include_router(mock_data.router)
api_router.include_router(cache.router)
api_router.include_router(health.api_router)

root_router = APIRouter()
root_router.include_router(health.root_router)
