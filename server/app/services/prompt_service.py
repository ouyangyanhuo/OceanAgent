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
        # Prompt 文件名与逻辑名称保持一致，例如 graph_expand_prompt.json。
        prompt = read_json(PROMPT_DIR / f"{name}.json", {})

        # 如果 template 缺失，直接抛 KeyError，让开发阶段尽早发现错误配置。
        return prompt["template"]

    def render(self, template: str, context: dict[str, Any]) -> str:
        """用上下文替换模板变量。

        dict/list 会转成格式化 JSON 字符串，方便 LLM 读取结构化上下文。
        """
        result = template
        for key, value in context.items():
            # 结构化数据用 JSON 表示，比 Python dict 字符串更适合放进 prompt。
            if isinstance(value, dict | list):
                replacement = json.dumps(value, ensure_ascii=False, indent=2)
            else:
                # 基础类型直接转字符串，例如 expand_type、max_nodes。
                replacement = str(value)

            # 模板变量格式固定为 {{key}}，不引入复杂模板引擎，降低依赖和认知成本。
            result = result.replace(f"{{{{{key}}}}}", replacement)
        return result

    def render_graph_expand_prompt(self, context: dict[str, Any]) -> str:
        """渲染图谱扩展 prompt。"""
        return self.render(self.load_prompt("graph_expand_prompt"), context)

    def render_create_seed_node_prompt(self, context: dict[str, Any]) -> str:
        """渲染新建种子节点 prompt。"""
        return self.render(self.load_prompt("create_seed_node_prompt"), context)

    def render_connect_nodes_prompt(self, context: dict[str, Any]) -> str:
        """渲染节点连接 prompt。"""
        return self.render(self.load_prompt("connect_nodes_prompt"), context)

    def render_agent_prompt(self, agent_type: str, context: dict[str, Any]) -> str:
        """按智能体类型渲染对应 prompt。"""
        # agent_type 到 prompt 文件名的映射放在这里，避免前端需要知道文件命名。
        prompt_file_by_agent = {
            "red_tide": "red_tide_prompt",
            "current_analysis": "current_analysis_prompt",
            "route_optimization": "route_optimization_prompt",
            "fishery_assessment": "fishery_assessment_prompt",
            "buoy_diagnosis": "buoy_diagnosis_prompt",
            "ecological_qa": "ecological_qa_prompt",
        }

        # agent_type 已由 AgentService 校验；直接索引可以让错误类型尽早暴露。
        return self.render(self.load_prompt(prompt_file_by_agent[agent_type]), context)

    def render_report_prompt(self, context: dict[str, Any]) -> str:
        """渲染报告生成 prompt。"""
        return self.render(self.load_prompt("report_prompt"), context)

    def render_keyword_prompt(self, context: dict[str, Any]) -> str:
        """渲染关键词提取 prompt。"""
        return self.render(self.load_prompt("ecological_qa_keyword_prompt"), context)
