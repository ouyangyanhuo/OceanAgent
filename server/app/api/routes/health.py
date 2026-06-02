"""健康检查 API。"""

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.response import success

root_router = APIRouter()
api_router = APIRouter()


def health_payload() -> dict[str, str]:
    """构造健康检查数据，供 /health 和 /api/health 复用。"""
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "version": settings.version}


@root_router.get("/health")
def health() -> dict:
    """根路径健康检查，便于部署或本地 curl 直接访问。"""
    return success(health_payload())


@api_router.get("/health")
def api_health() -> dict:
    """API 前缀下的健康检查，便于前端按统一前缀访问。"""
    return success(health_payload())
