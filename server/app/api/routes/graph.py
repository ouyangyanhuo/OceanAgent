from fastapi import APIRouter, Query

from app.core.response import success
from app.models.graph import ExpandNodeRequest
from app.services.expansion_service import ExpansionService
from app.services.graph_service import GraphService
from app.services.validation_service import ValidationService

router = APIRouter(prefix="/graph", tags=["graph"])
graph_service = GraphService()
expansion_service = ExpansionService()
validation_service = ValidationService()


@router.get("")
def get_graph() -> dict:
    return success(graph_service.get_graph().model_dump(mode="json"))


@router.get("/nodes/{node_id}")
def get_node(node_id: str) -> dict:
    return success(graph_service.get_node(node_id).model_dump(mode="json"))


@router.get("/nodes/{node_id}/neighbors")
def get_neighbors(node_id: str, depth: int = Query(default=1, ge=1, le=3)) -> dict:
    neighbors = graph_service.get_neighbors(node_id, depth=depth)
    return success(
        {
            "nodes": [node.model_dump(mode="json") for node in neighbors["nodes"]],
            "edges": [edge.model_dump(mode="json") for edge in neighbors["edges"]],
        }
    )


@router.get("/nodes/{node_id}/expand-options")
def get_expand_options(node_id: str) -> dict:
    node = graph_service.get_node(node_id)
    rules = validation_service.load_schema_rules().get("expand_types", {})
    return success(
        {
            "node_id": node_id,
            "options": [
                {
                    "expand_type": expand_type,
                    "label": rule.get("label", expand_type),
                    "expanded": node.expanded.get(expand_type, False),
                }
                for expand_type, rule in rules.items()
            ],
        }
    )


@router.post("/expand")
def expand_node(request: ExpandNodeRequest) -> dict:
    response = expansion_service.expand_node(
        request.node_id,
        request.expand_type,
        force_refresh=request.force_refresh,
    )
    return success(response.model_dump(mode="json"))
