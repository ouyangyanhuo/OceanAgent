"""报告生成服务。

报告属于表达层内容，可以缓存；它不会改变 graph.json。
"""

from datetime import datetime
from typing import Any

from app.core.errors import ValidationError
from app.models.report import ReportGenerateResponse
from app.services.ai_service import AIService
from app.services.cache_service import CacheService
from app.services.graph_service import GraphService
from app.services.mock_ocean_service import MockOceanService


# 支持的报告类型与中文标题后缀。
REPORT_TITLES = {
    "red_tide_report": "赤潮风险分析报告",
    "current_report": "海流趋势分析报告",
    "fishery_report": "渔场环境评估报告",
    "route_report": "航线优化分析报告",
    "comprehensive_report": "海洋综合分析报告",
}


class ReportService:
    """封装报告上下文构造、缓存和 Markdown 生成。"""

    def __init__(self) -> None:
        """初始化报告依赖的服务。"""
        self.graph_service = GraphService()
        self.mock_ocean_service = MockOceanService()
        self.ai_service = AIService()
        self.cache_service = CacheService()

    def generate_report(
        self,
        report_type: str,
        node_id: str | None,
        params: dict[str, Any] | None = None,
    ) -> ReportGenerateResponse:
        """生成指定类型的 Markdown 报告。"""
        if report_type not in REPORT_TITLES:
            # 报告类型必须固定，避免前端或 LLM 自由创造无法渲染/无法缓存的类型。
            raise ValidationError(f"Unsupported report_type: {report_type}", code="INVALID_REPORT_TYPE")

        # params 归一化成字典，保证缓存 key 和上下文结构稳定。
        params = params or {}

        # node_id 可选；有 node_id 时报告标题和 related_nodes 都围绕该节点。
        node = self.graph_service.get_node(node_id).model_dump(mode="json") if node_id else None
        title = self._title(report_type, node)

        # 报告上下文聚合图谱节点和模拟海洋数据，后续可直接传给真实 LLM。
        context = {
            "report_type": report_type,
            "title": title,
            "node": node,
            "params": params,
            "observations": self.mock_ocean_service.get_observations(node_id),
            "buoys": self.mock_ocean_service.get_buoy_status(),
            "current_fields": self.mock_ocean_service.get_current_fields(node_id),
            "fishery_areas": self.mock_ocean_service.get_fishery_areas(),
        }

        # 报告是表达层结果，可以使用缓存减少重复生成。
        cache_key = self.cache_service.make_key(report_type, node_id, params)
        cached = self.cache_service.get("report", cache_key)
        if cached:
            # 缓存内容来自旧 response，返回时覆盖 used_cache=True 让前端知道命中缓存。
            return ReportGenerateResponse.model_validate(cached | {"used_cache": True})

        # 当前生成 mock Markdown；未来真实 LLM 也应只生成表达层内容，不改图谱。
        markdown = self.ai_service.generate_report(context)
        response = ReportGenerateResponse(
            report_type=report_type,
            title=title,
            markdown=markdown,
            related_nodes=[node] if node else [],
            created_at=datetime.utcnow().replace(microsecond=0).isoformat(),
            used_cache=False,
        )

        # 缓存写入 JSON 结构，避免把 Pydantic 对象直接塞进文件。
        self.cache_service.set("report", cache_key, response.model_dump(mode="json"))
        return response

    def _title(self, report_type: str, node: dict[str, Any] | None) -> str:
        """生成报告标题。"""
        if node:
            # 有节点时标题带节点名称，便于用户区分报告对象。
            return f"{node['name']}{REPORT_TITLES[report_type]}"
        return REPORT_TITLES[report_type]
