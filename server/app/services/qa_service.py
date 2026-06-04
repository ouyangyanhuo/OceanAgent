"""生态问答 RAG 服务。

编排流程：用户问题 → 关键词提取(LLM) → 图谱检索 → 上下文构建 → 流式回答(LLM)。
当 LLM 不可用时退化为 mock 模式。
"""

import json
import logging
import re
import time
from collections.abc import Generator
from typing import Any

from app.core.config import get_settings
from app.services.graph_service import GraphService
from app.services.llm_client import LLMClient
from app.services.mock_ocean_service import MockOceanService
from app.services.prompt_service import PromptService

logger = logging.getLogger(__name__)


class QaService:
    """生态问答 RAG 服务，负责关键词提取、图谱检索和流式回答生成。"""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.graph_service = GraphService()
        self.mock_ocean_service = MockOceanService()
        self.prompt_service = PromptService()

        if not self.settings.use_mock_llm:
            self.llm_client = LLMClient(
                base_url=self.settings.llm_base_url,
                api_key=self.settings.llm_api_key,
                model=self.settings.llm_model,
                timeout=self.settings.llm_timeout,
            )
            logger.info("[QaService] ✅ 真实 LLM 模式: %s / %s", self.settings.llm_base_url, self.settings.llm_model)
        else:
            self.llm_client = None
            logger.info("[QaService] ⚠️  Mock 模式")

    # ── 公开接口 ──────────────────────────────────────────────

    def stream_answer(self, query: str) -> Generator[str, None, None]:
        """生态问答主流程：关键词提取 → 图谱检索 → 流式回答。

        Yields SSE 格式的字符串，每条以 "data: " 开头，末尾 \\n\\n。
        - status 事件：阶段状态（keyword / search / think）
        - content 事件：回答文本增量
        - done 事件：包含 related_nodes / related_edges 的结束标记
        """
        # ① 关键词提取
        yield self._sse_event("status", {"phase": "keyword", "message": "正在提取关键词..."})
        keywords = self._extract_keywords(query)
        logger.info("[QaService] 提取关键词: %s", keywords)

        # ② 图谱检索
        yield self._sse_event("status", {"phase": "search", "message": "正在检索知识图谱..."})
        graph_context = self.graph_service.search_by_keywords(keywords)
        related_nodes = [n.model_dump(mode="json") if hasattr(n, "model_dump") else n for n in graph_context["nodes"]]
        related_edges = [e.model_dump(mode="json") if hasattr(e, "model_dump") else e for e in graph_context["edges"]]
        matched_nodes = graph_context.get("matched_nodes", [])
        logger.info("[QaService] 图谱检索命中 %d 个节点，展开 %d 个节点、%d 条边",
                     len(matched_nodes), len(related_nodes), len(related_edges))

        # ③ 构建上下文并流式生成回答
        yield self._sse_event("status", {"phase": "think", "message": "AI 正在思考..."})
        if self.llm_client:
            yield from self._real_stream_answer(query, related_nodes, related_edges)
        else:
            yield from self._mock_stream_answer(query, related_nodes, related_edges)

    # ── 关键词提取 ────────────────────────────────────────────

    def _extract_keywords(self, query: str) -> list[str]:
        """从用户问题中提取 1-2 个核心关键词。

        优先使用 LLM 提取；LLM 不可用时使用简单分词兜底。
        """
        if self.llm_client:
            try:
                prompt = self.prompt_service.render_keyword_prompt({"query": query})
                raw = self.llm_client.chat_json(
                    user_prompt=prompt,
                    temperature=0.1,
                )
                keywords = raw.get("keywords", [])
                if isinstance(keywords, list) and keywords:
                    return [str(kw).strip() for kw in keywords[:3] if kw]
            except Exception:
                logger.warning("LLM 关键词提取失败，退化为简单分词", exc_info=True)

        # 兜底：简单中文分词 —— 提取连续中文字符片段（2字以上）
        return self._simple_tokenize(query)

    @staticmethod
    def _simple_tokenize(text: str) -> list[str]:
        """简单中文分词兜底：提取 2 字以上的连续中文片段。"""
        tokens = re.findall(r"[一-鿿]{2,}", text)
        return tokens[:3] if tokens else [text[:4]]

    # ── 流式回答生成 ──────────────────────────────────────────

    def _build_context(self, query: str, related_nodes: list, related_edges: list) -> dict[str, Any]:
        """构建 LLM 回答所需的上下文。"""
        # 取第一个匹配节点作为主节点，没有则用空字典。
        node = related_nodes[0] if related_nodes else {}
        return {
            "agent_type": "ecological_qa",
            "query": query,
            "node": node,
            "params": {},
            "related_nodes": related_nodes,
            "related_edges": related_edges,
            "observations": self.mock_ocean_service.get_observations(),
            "fishery_areas": self.mock_ocean_service.get_fishery_areas(),
        }

    def _real_stream_answer(
        self, query: str, related_nodes: list, related_edges: list,
    ) -> Generator[str, None, None]:
        """调用真实 LLM 流式接口生成回答。"""
        context = self._build_context(query, related_nodes, related_edges)
        prompt = self.prompt_service.render_agent_prompt("ecological_qa", context)

        try:
            for chunk in self.llm_client.chat_text_stream(
                user_prompt=prompt,
                temperature=0.5,
            ):
                yield self._sse_event("content", {"text": chunk})
        except Exception:
            logger.error("LLM 流式回答生成失败", exc_info=True)
            yield self._sse_event("content", {"text": "\n\n⚠️ LLM 回答生成失败，请检查配置后重试。"})

        # 流结束，发送 related_nodes 和 related_edges
        yield self._sse_event("done", {
            "related_nodes": related_nodes[:5],
            "related_edges": related_edges[:10],
        })

    def _mock_stream_answer(
        self, query: str, related_nodes: list, related_edges: list,
    ) -> Generator[str, None, None]:
        """Mock 模式：逐字输出预设回答，模拟流式效果。"""
        node_name = (related_nodes[0].get("name") if related_nodes else None) or "目标海域"
        answer = (
            f"根据知识图谱检索结果，关于「{query}」的回答如下：\n\n"
            f"结合图谱中 {node_name} 及其关联节点的生态关系分析，"
            f"该问题涉及海洋生态系统的多个关键因素，包括水温、盐度、营养盐输入和生物群落结构。"
            f"建议结合浮标监测数据和遥感观测进行综合评估。"
        )

        for char in answer:
            yield self._sse_event("content", {"text": char})
            time.sleep(0.02)

        yield self._sse_event("done", {
            "related_nodes": related_nodes[:5],
            "related_edges": related_edges[:10],
        })

    @staticmethod
    def _sse_event(event: str, data: dict[str, Any]) -> str:
        """构造 SSE 格式事件字符串。"""
        return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
