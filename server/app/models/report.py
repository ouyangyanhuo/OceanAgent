"""报告接口模型。"""

from typing import Any

from pydantic import BaseModel, Field


class ReportGenerateRequest(BaseModel):
    """生成报告请求。"""

    report_type: str
    node_id: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class ReportGenerateResponse(BaseModel):
    """生成报告响应。

    markdown 字段直接返回可渲染的 Markdown 文本。
    """

    report_type: str
    title: str
    markdown: str
    related_nodes: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str
    used_cache: bool = False
