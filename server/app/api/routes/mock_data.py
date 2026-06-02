"""模拟海洋数据 API。

这些接口读取 app/data/mock 下的 JSON 文件，给前端页面和调试使用。
"""

from fastapi import APIRouter

from app.core.response import success
from app.services.mock_ocean_service import MockOceanService

router = APIRouter(prefix="/mock", tags=["mock"])
mock_ocean_service = MockOceanService()


@router.get("/ocean-observations")
def ocean_observations(sea_area_id: str | None = None) -> dict:
    """返回海洋观测记录，可按 sea_area_id 过滤。"""
    return success(mock_ocean_service.get_observations(sea_area_id))


@router.get("/buoy-status")
def buoy_status(buoy_id: str | None = None) -> dict:
    """返回浮标状态，可按 buoy_id 过滤。"""
    return success(mock_ocean_service.get_buoy_status(buoy_id))


@router.get("/current-fields")
def current_fields(sea_area_id: str | None = None) -> dict:
    """返回海流场数据，可按 sea_area_id 过滤。"""
    return success(mock_ocean_service.get_current_fields(sea_area_id))


@router.get("/fishery-areas")
def fishery_areas() -> dict:
    """返回渔场区域 mock 数据。"""
    return success(mock_ocean_service.get_fishery_areas())


@router.get("/routes")
def routes() -> dict:
    """返回航线 mock 数据。"""
    return success(mock_ocean_service.get_routes())
