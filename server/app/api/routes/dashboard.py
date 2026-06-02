"""仪表盘 API。

该接口保留早期前端需要的完整 mock dashboard 数据结构，
暂时不走统一 success 包装，避免破坏现有前端对接。
"""

from fastapi import APIRouter

from app.mock_data import DASHBOARD_DATA

router = APIRouter()


@router.get("/dashboard")
def dashboard() -> dict:
    """返回首页仪表盘 mock 数据。"""
    return DASHBOARD_DATA
