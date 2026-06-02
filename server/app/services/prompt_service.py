import json
from typing import Any

from app.core.json_store import read_json
from app.core.paths import PROMPT_DIR


class PromptService:
    def load_prompt(self, name: str) -> str:
        prompt = read_json(PROMPT_DIR / f"{name}.json", {})
        return prompt["template"]

    def render(self, template: str, context: dict[str, Any]) -> str:
        result = template
        for key, value in context.items():
            if isinstance(value, dict | list):
                replacement = json.dumps(value, ensure_ascii=False, indent=2)
            else:
                replacement = str(value)
            result = result.replace(f"{{{{{key}}}}}", replacement)
        return result

    def render_graph_expand_prompt(self, context: dict[str, Any]) -> str:
        return self.render(self.load_prompt("graph_expand_prompt"), context)

    def render_agent_prompt(self, agent_type: str, context: dict[str, Any]) -> str:
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
        return self.render(self.load_prompt("report_prompt"), context)
