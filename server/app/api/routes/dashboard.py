from fastapi import APIRouter

from app.mock_data import DASHBOARD_DATA

router = APIRouter()


@router.get("/dashboard")
def dashboard() -> dict:
    return DASHBOARD_DATA
