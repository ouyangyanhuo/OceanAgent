from fastapi import APIRouter

from app.core.config import get_settings
from app.core.response import success

root_router = APIRouter()
api_router = APIRouter()


def health_payload() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "version": settings.version}


@root_router.get("/health")
def health() -> dict:
    return success(health_payload())


@api_router.get("/health")
def api_health() -> dict:
    return success(health_payload())
