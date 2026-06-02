"""图谱相关 API。

路由层只负责解析请求和序列化响应；图谱读写、扩展和校验都委托给 service。
"""

from fastapi import APIRouter, Query

from app.core.response import success
from app.models.graph import ExpandNodeRequest
from app.services.expansion_service import ExpansionService
from app.services.graph_service import GraphService
from app.services.validation_service import ValidationService

router = APIRouter(prefix="/graph", tags=["graph"])

# 第一版服务对象无请求级状态，可以作为模块级单例复用。
graph_service = GraphService()
expansion_service = ExpansionService()
validation_service = ValidationService()


@router.get("")
def get_graph() -> dict:
    """获取完整图谱。"""
    # mode="json" 会把模型转换为前端可直接消费的 dict/list/str/number。
    return success(graph_service.get_graph().model_dump(mode="json"))


@router.get("/nodes/{node_id}")
def get_node(node_id: str) -> dict:
    """获取单个节点详情。"""
    return success(graph_service.get_node(node_id).model_dump(mode="json"))


@router.get("/nodes/{node_id}/neighbors")
def get_neighbors(node_id: str, depth: int = Query(default=1, ge=1, le=3)) -> dict:
    """获取节点邻居。

    depth 在 API 层限制为 1 到 3，避免一次请求展开过大范围。
    """
    neighbors = graph_service.get_neighbors(node_id, depth=depth)

    # GraphService 返回 Pydantic 对象，这里统一序列化为 JSON 兼容结构。
    return success(
        {
            "nodes": [node.model_dump(mode="json") for node in neighbors["nodes"]],
            "edges": [edge.model_dump(mode="json") for edge in neighbors["edges"]],
        }
    )


@router.get("/nodes/{node_id}/expand-options")
def get_expand_options(node_id: str) -> dict:
    """返回某个节点可执行的扩展方向以及是否已扩展。"""
    # 先读取节点，既能确认 node_id 存在，也能获取该节点 expanded 状态。
    node = graph_service.get_node(node_id)

    # 扩展选项来自 schema_rules，而不是写死在前端或路由里。
    rules = validation_service.load_schema_rules().get("expand_types", {})
    return success(
        {
            "node_id": node_id,
            "options": [
                {
                    "expand_type": expand_type,
                    # label 供前端直接展示；缺失时用 expand_type 兜底。
                    "label": rule.get("label", expand_type),
                    # expanded 用于前端控制“已扩展/可扩展”状态。
                    "expanded": node.expanded.get(expand_type, False),
                }
                for expand_type, rule in rules.items()
            ],
        }
    )


@router.post("/expand")
def expand_node(request: ExpandNodeRequest) -> dict:
    """扩展节点。

    ExpansionService 会负责检查 expansion_index、调用 mock AI、校验候选结果、
    写入 graph.json、更新 expansion_index 并创建快照。
    """
    # request 已由 Pydantic 校验基础字段类型；业务校验交给 ExpansionService。
    response = expansion_service.expand_node(
        request.node_id,
        request.expand_type,
        force_refresh=request.force_refresh,
    )
    return success(response.model_dump(mode="json"))
