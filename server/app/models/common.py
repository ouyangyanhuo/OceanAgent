from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str = "ok"
    error: dict[str, Any] | None = None


class CacheClearRequest(BaseModel):
    cache_name: str | None = Field(default=None, description="ai, report, agent, or omitted for all")
