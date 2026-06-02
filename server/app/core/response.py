from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from .errors import AppError


def success(data: Any = None, message: str = "ok") -> dict[str, Any]:
    return {"success": True, "data": data, "message": message, "error": None}


def failure(code: str, detail: str, message: str = "failed") -> dict[str, Any]:
    return {
        "success": False,
        "data": None,
        "message": message,
        "error": {"code": code, "detail": detail},
    }


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    status_code = 404 if exc.code == "NOT_FOUND" else 400
    return JSONResponse(status_code=status_code, content=failure(exc.code, exc.detail))
