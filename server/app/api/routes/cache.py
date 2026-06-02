from fastapi import APIRouter

from app.core.response import success
from app.models.common import CacheClearRequest
from app.services.cache_service import CacheService

router = APIRouter(prefix="/cache", tags=["cache"])
cache_service = CacheService()


@router.get("/status")
def cache_status() -> dict:
    return success(cache_service.status())


@router.post("/clear")
def clear_cache(request: CacheClearRequest) -> dict:
    cache_service.clear(request.cache_name)
    return success({"cleared": request.cache_name or "all"})
