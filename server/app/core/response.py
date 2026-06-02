"""统一 API 响应格式。

所有业务接口尽量返回 success()/failure() 的结构，方便前端统一处理。
"""

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from .errors import AppError


def success(data: Any = None, message: str = "ok") -> dict[str, Any]:
    """构造成功响应。"""
    return {"success": True, "data": data, "message": message, "error": None}


def failure(code: str, detail: str, message: str = "failed") -> dict[str, Any]:
    """构造失败响应。"""
    return {
        "success": False,
        "data": None,
        "message": message,
        "error": {"code": code, "detail": detail},
    }


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    """将业务异常转换为 HTTP JSON 响应。"""
    status_code = 404 if exc.code == "NOT_FOUND" else 400
    return JSONResponse(status_code=status_code, content=failure(exc.code, exc.detail))
