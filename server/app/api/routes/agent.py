from fastapi import APIRouter

from app.core.response import success
from app.models.agent import AgentRunRequest
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agent", tags=["agent"])
agent_service = AgentService()


@router.get("/list")
def list_agents() -> dict:
    return success([agent.model_dump(mode="json") for agent in agent_service.list_agents()])


@router.post("/run")
def run_agent(request: AgentRunRequest) -> dict:
    response = agent_service.run_agent(
        request.agent_type,
        request.query,
        node_id=request.node_id,
        params=request.params,
    )
    return success(response.model_dump(mode="json"))
