from typing import Any

from pydantic import BaseModel, Field


class ReportGenerateRequest(BaseModel):
    report_type: str
    node_id: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class ReportGenerateResponse(BaseModel):
    report_type: str
    title: str
    markdown: str
    related_nodes: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str
    used_cache: bool = False
