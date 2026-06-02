"""缓存管理 API。

缓存只用于表达层结果，例如智能体回答和报告；图谱结构扩展由 expansion_index 控制。
"""

from fastapi import APIRouter

from app.core.response import success
from app.models.common import CacheClearRequest
from app.services.cache_service import CacheService

router = APIRouter(prefix="/cache", tags=["cache"])
cache_service = CacheService()


@router.get("/status")
def cache_status() -> dict:
    """返回各缓存文件是否存在以及当前条目数量。"""
    return success(cache_service.status())


@router.post("/clear")
def clear_cache(request: CacheClearRequest) -> dict:
    """清空指定缓存；不传 cache_name 时清空全部缓存。"""
    cache_service.clear(request.cache_name)
    return success({"cleared": request.cache_name or "all"})
