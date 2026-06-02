"""通用请求/响应模型。"""

from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """统一响应结构的 Pydantic 版本。

    当前路由主要使用 core.response.success() 返回 dict，
    该模型保留给后续 OpenAPI response_model 或测试使用。
    """

    success: bool = True
    data: Any = None
    message: str = "ok"
    error: dict[str, Any] | None = None


class CacheClearRequest(BaseModel):
    """清空缓存请求。

    cache_name 为空时表示清空全部缓存。
    """

    cache_name: str | None = Field(default=None, description="ai, report, agent, or omitted for all")
