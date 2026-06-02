from typing import Any

from pydantic import BaseModel, Field


class AgentInfo(BaseModel):
    agent_type: str
    name: str
    description: str
    tags: list[str] = Field(default_factory=list)


class AgentRunRequest(BaseModel):
    agent_type: str
    query: str
    node_id: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class AgentStep(BaseModel):
    name: str
    status: str = "done"


class AgentRunResponse(BaseModel):
    agent_type: str
    answer: str
    related_nodes: list[dict[str, Any]] = Field(default_factory=list)
    related_edges: list[dict[str, Any]] = Field(default_factory=list)
    used_cache: bool = False
    steps: list[AgentStep] = Field(default_factory=list)
