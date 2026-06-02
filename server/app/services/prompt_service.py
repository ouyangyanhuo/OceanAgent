"""Prompt 模板服务。

Prompt 统一存储为 app/data/prompts/*.json。
每个 JSON 文件至少包含 template 字段，本服务只读取 template 并做简单变量替换。
"""

import json
from typing import Any

from app.core.json_store import read_json
from app.core.paths import PROMPT_DIR


class PromptService:
    """加载和渲染 Prompt 模板。"""

    def load_prompt(self, name: str) -> str:
        """按名称读取 prompt JSON 的 template 字段。"""
        prompt = read_json(PROMPT_DIR / f"{name}.json", {})
        return prompt["template"]

    def render(self, template: str, context: dict[str, Any]) -> str:
        """用上下文替换模板变量。

        dict/list 会转成格式化 JSON 字符串，方便 LLM 读取结构化上下文。
        """
        result = template
        for key, value in context.items():
            if isinstance(value, dict | list):
                replacement = json.dumps(value, ensure_ascii=False, indent=2)
            else:
                replacement = str(value)
            result = result.replace(f"{{{{{key}}}}}", replacement)
        return result

    def render_graph_expand_prompt(self, context: dict[str, Any]) -> str:
        """渲染图谱扩展 prompt。"""
        return self.render(self.load_prompt("graph_expand_prompt"), context)

    def render_agent_prompt(self, agent_type: str, context: dict[str, Any]) -> str:
        """按智能体类型渲染对应 prompt。"""
        prompt_file_by_agent = {
            "red_tide": "red_tide_prompt",
            "current_analysis": "current_analysis_prompt",
            "route_optimization": "route_optimization_prompt",
            "fishery_assessment": "fishery_assessment_prompt",
            "buoy_diagnosis": "buoy_diagnosis_prompt",
            "ecological_qa": "ecological_qa_prompt",
        }
        return self.render(self.load_prompt(prompt_file_by_agent[agent_type]), context)

    def render_report_prompt(self, context: dict[str, Any]) -> str:
        """渲染报告生成 prompt。"""
        return self.render(self.load_prompt("report_prompt"), context)
