"""智能体 API。

智能体固定流程服务，路由只暴露列表和运行入口。
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.response import success
from app.models.agent import AgentRunRequest, QaStreamRequest
from app.services.agent_service import AgentService
from app.services.qa_service import QaService

router = APIRouter(prefix="/agent", tags=["agent"])

# AgentService 当前不保存请求级状态，可以作为模块级实例复用。
agent_service = AgentService()
qa_service = QaService()


@router.get("/list")
def list_agents() -> dict:
    """返回前端可展示和选择的智能体列表。"""
    # AgentInfo 是 Pydantic 模型，返回前先转成普通 JSON 结构。
    return success([agent.model_dump(mode="json") for agent in agent_service.list_agents()])


@router.post("/run")
def run_agent(request: AgentRunRequest) -> dict:
    """运行指定智能体。

    具体上下文构造、缓存读取和 mock AI 回答都在 AgentService 中完成。
    """
    # 路由层不拼接 steps 或回答内容，只把请求字段转交给服务层。
    response = agent_service.run_agent(
        request.agent_type,
        request.query,
        node_id=request.node_id,
        params=request.params,
    )
    return success(response.model_dump(mode="json"))


@router.post("/qa/stream")
def qa_stream(request: QaStreamRequest) -> StreamingResponse:
    """生态问答流式端点。

    返回 SSE (text/event-stream) 格式：
    - event: content  → data: {"text": "..."}   (回答文本增量)
    - event: done     → data: {"related_nodes": [...], "related_edges": [...]}  (结束标记)
    """
    return StreamingResponse(
        qa_service.stream_answer(request.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
