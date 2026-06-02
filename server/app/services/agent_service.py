"""智能体调度服务。

第一版不引入复杂 Agent 框架，而是固定流程：
任务解析 -> 图谱检索 -> 模拟数据读取 -> AI 分析。
"""

from typing import Any

from app.core.errors import ValidationError
from app.models.agent import AgentInfo, AgentRunResponse, AgentStep
from app.services.ai_service import AIService
from app.services.cache_service import CacheService
from app.services.graph_service import GraphService
from app.services.mock_ocean_service import MockOceanService


# 前端可见的智能体注册表。新增智能体时先在这里声明基本信息。
AGENTS = [
    AgentInfo(
        agent_type="red_tide",
        name="赤潮预警智能体",
        description="赤潮监测、识别与预测的专业智能体",
        tags=["生态分析", "灾害预警"],
    ),
    AgentInfo(
        agent_type="current_analysis",
        name="海流分析智能体",
        description="基于多源数据的海流动力分析与趋势预测智能体",
        tags=["海洋监测", "海流分析"],
    ),
    AgentInfo(
        agent_type="route_optimization",
        name="航线优化智能体",
        description="基于气象海况的航线规划与优化智能体",
        tags=["航运预测", "航线优化"],
    ),
    AgentInfo(
        agent_type="ecological_qa",
        name="海洋生态问答智能体",
        description="海洋生态知识问答与解读智能体",
        tags=["生态分析", "知识问答"],
    ),
    AgentInfo(
        agent_type="buoy_diagnosis",
        name="浮标数据诊断智能体",
        description="浮标异常监测与数据质量诊断智能体",
        tags=["设备巡检", "数据诊断"],
    ),
    AgentInfo(
        agent_type="fishery_assessment",
        name="渔场评估智能体",
        description="渔场环境评估与渔获量预测智能体",
        tags=["渔业分析", "资源评估"],
    ),
]


class AgentService:
    """封装智能体列表、上下文构造、缓存和回答生成。"""

    def __init__(self) -> None:
        """初始化智能体依赖的服务。"""
        self.graph_service = GraphService()
        self.mock_ocean_service = MockOceanService()
        self.ai_service = AIService()
        self.cache_service = CacheService()

    def list_agents(self) -> list[AgentInfo]:
        """返回全部已注册智能体。"""
        return AGENTS

    def run_agent(
        self,
        agent_type: str,
        query: str,
        node_id: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> AgentRunResponse:
        """运行指定智能体。

        先校验 agent_type，再构造上下文并尝试读取缓存；
        未命中缓存时调用 AIService 生成 mock 回答。
        """
        if agent_type not in {agent.agent_type for agent in AGENTS}:
            # 尽早失败，避免后续构造无意义上下文或写入错误缓存。
            raise ValidationError(f"Unsupported agent_type: {agent_type}", code="INVALID_AGENT_TYPE")

        # params 统一归一化成字典，后续上下文和缓存 key 可以稳定处理。
        params = params or {}
        context = self.build_agent_context(agent_type, query, node_id, params)

        # 缓存 key 由智能体类型、用户问题、节点上下文和参数共同决定。
        cache_key = self.cache_service.make_key(agent_type, query, context.get("node"), params)
        cached = self.cache_service.get("agent", cache_key)
        if cached:
            # 缓存中保存的是 response 的 JSON 结构，这里重新校验成 Pydantic 模型。
            return AgentRunResponse.model_validate(cached | {"used_cache": True})

        # steps 是前端展示“智能体执行过程”的固定流程。
        answer = self.ai_service.generate_agent_answer(context)
        response = AgentRunResponse(
            agent_type=agent_type,
            answer=answer,
            related_nodes=context["related_nodes"],
            related_edges=context["related_edges"],
            used_cache=False,
            steps=[
                AgentStep(name="任务解析"),
                AgentStep(name="图谱检索"),
                AgentStep(name="数据读取"),
                AgentStep(name="AI 分析"),
            ],
        )

        # 写缓存时存 JSON 结构，而不是 Pydantic 对象，保证文件内容可直接序列化。
        self.cache_service.set("agent", cache_key, response.model_dump(mode="json"))
        return response

    def build_agent_context(
        self,
        agent_type: str,
        query: str,
        node_id: str | None,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """构造智能体分析上下文。

        上下文由图谱节点、一跳邻居、模拟观测数据、浮标状态、海流、渔场和航线组成。
        """
        # node_id 可选：没有 node_id 时，智能体只基于 query、params 和 mock 数据分析。
        node = self.graph_service.get_node(node_id).model_dump(mode="json") if node_id else None

        # 有节点时读取一跳邻居作为局部知识图谱上下文；没有节点时使用空上下文。
        neighbors = self.graph_service.get_neighbors(node_id, depth=1) if node_id else {"nodes": [], "edges": []}

        # 只有当前节点本身是 SeaArea 时，才直接把 node_id 当作海域 ID。
        sea_area_id = node_id if node and node.get("type") == "SeaArea" else params.get("sea_area_id")
        return {
            # 原始请求信息保留在上下文中，方便 prompt 或 mock 逻辑使用。
            "agent_type": agent_type,
            "query": query,
            "node": node,
            "params": params,

            # 图谱上下文转成 JSON dict，避免下游 AIService 依赖 Pydantic 类型。
            "related_nodes": [item.model_dump(mode="json") for item in neighbors["nodes"]],
            "related_edges": [item.model_dump(mode="json") for item in neighbors["edges"]],

            # 领域 mock 数据按 sea_area_id 过滤，尽量让回答与当前海域相关。
            "observations": self.mock_ocean_service.get_observations(sea_area_id),
            "buoys": self.mock_ocean_service.get_buoy_status(),
            "current_fields": self.mock_ocean_service.get_current_fields(sea_area_id),
            "fishery_areas": self.mock_ocean_service.get_fishery_areas(),
            "routes": self.mock_ocean_service.get_routes(),
        }
