from fastapi import APIRouter

from app.core.response import success
from app.services.mock_ocean_service import MockOceanService

router = APIRouter(prefix="/mock", tags=["mock"])
mock_ocean_service = MockOceanService()


@router.get("/ocean-observations")
def ocean_observations(sea_area_id: str | None = None) -> dict:
    return success(mock_ocean_service.get_observations(sea_area_id))


@router.get("/buoy-status")
def buoy_status(buoy_id: str | None = None) -> dict:
    return success(mock_ocean_service.get_buoy_status(buoy_id))


@router.get("/current-fields")
def current_fields(sea_area_id: str | None = None) -> dict:
    return success(mock_ocean_service.get_current_fields(sea_area_id))


@router.get("/fishery-areas")
def fishery_areas() -> dict:
    return success(mock_ocean_service.get_fishery_areas())


@router.get("/routes")
def routes() -> dict:
    return success(mock_ocean_service.get_routes())
