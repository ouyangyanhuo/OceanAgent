"""报告 API。"""

from fastapi import APIRouter

from app.core.response import success
from app.models.report import ReportGenerateRequest
from app.services.report_service import ReportService

router = APIRouter(prefix="/report", tags=["report"])
report_service = ReportService()


@router.post("/generate")
def generate_report(request: ReportGenerateRequest) -> dict:
    """生成 Markdown 分析报告。"""
    # ReportService 负责校验 report_type、构造上下文、读写缓存和生成 Markdown。
    response = report_service.generate_report(
        request.report_type,
        request.node_id,
        params=request.params,
    )
    return success(response.model_dump(mode="json"))
