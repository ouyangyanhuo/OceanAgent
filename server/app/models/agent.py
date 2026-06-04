"""智能体接口模型。

第一版智能体是固定流程的伪 Agent，不引入复杂多智能体框架。
"""

from typing import Any

from pydantic import BaseModel, Field


class AgentInfo(BaseModel):
    """智能体列表项。"""

    agent_type: str
    name: str
    description: str
    tags: list[str] = Field(default_factory=list)


class AgentRunRequest(BaseModel):
    """调用智能体的请求体。"""

    agent_type: str
    query: str
    node_id: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class AgentStep(BaseModel):
    """前端展示用的智能体执行步骤。"""

    name: str
    status: str = "done"


class AgentRunResponse(BaseModel):
    """智能体运行结果。"""

    agent_type: str
    answer: str
    related_nodes: list[dict[str, Any]] = Field(default_factory=list)
    related_edges: list[dict[str, Any]] = Field(default_factory=list)
    used_cache: bool = False
    steps: list[AgentStep] = Field(default_factory=list)


class QaStreamRequest(BaseModel):
    """生态问答流式请求体。"""

    query: str
