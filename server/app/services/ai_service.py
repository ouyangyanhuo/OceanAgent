from typing import Any


class AIService:
    def generate_graph_seed(self, topic: str) -> dict[str, Any]:
        return {
            "nodes": [
                {
                    "type": "SeaArea",
                    "name": topic,
                    "properties": {"description": f"{topic} 的种子海域节点。"},
                }
            ],
            "edges": [],
            "summary": "已生成 mock 种子图谱候选数据。",
        }

    def generate_graph_expansion(self, context: dict[str, Any]) -> dict[str, Any]:
        # Real LLM providers can be wired here later; v1 always stays runnable in mock mode.
        return self._mock_graph_expansion(context)

    def generate_agent_answer(self, context: dict[str, Any]) -> str:
        return self._mock_agent_answer(context)

    def generate_report(self, context: dict[str, Any]) -> str:
        return self._mock_report(context)

    def _mock_graph_expansion(self, context: dict[str, Any]) -> dict[str, Any]:
        expand_type = context["expand_type"]
        center_name = context["current_node"]["name"]
        if expand_type == "risk_factors":
            return {
                "nodes": [
                    {
                        "type": "RiskFactor",
                        "name": "叶绿素浓度升高",
                        "properties": {
                            "description": "叶绿素浓度升高可能表示浮游植物异常繁殖。",
                            "risk_weight": 0.82,
                            "confidence": 0.76,
                        },
                    },
                    {
                        "type": "PreventionMeasure",
                        "name": "加强近岸营养盐排放管控",
                        "properties": {
                            "description": "通过削减近岸营养盐输入降低赤潮风险。",
                            "priority": "high",
                        },
                    },
                ],
                "edges": [
                    {
                        "source_ref": context["current_node"]["id"],
                        "target_name": "叶绿素浓度升高",
                        "relation": "affected_by",
                        "weight": 0.84,
                        "properties": {"description": f"{center_name} 受到叶绿素浓度升高影响。"},
                    },
                    {
                        "source_ref": "叶绿素浓度升高",
                        "target_name": "加强近岸营养盐排放管控",
                        "relation": "mitigated_by",
                        "weight": 0.66,
                        "properties": {"description": "管控措施可缓解赤潮风险因子。"},
                    },
                ],
                "summary": "识别出叶绿素浓度升高等赤潮风险因子。",
            }
        if expand_type == "monitoring_buoys":
            return {
                "nodes": [
                    {
                        "type": "Buoy",
                        "name": f"{center_name} 综合监测浮标",
                        "properties": {"status": "planned", "battery": 100},
                    },
                    {
                        "type": "Observation",
                        "name": f"{center_name} 溶解氧观测",
                        "properties": {"metric": "dissolved_oxygen", "value": 6.4, "unit": "mg/L"},
                    },
                ],
                "edges": [
                    {
                        "source_ref": context["current_node"]["id"],
                        "target_name": f"{center_name} 综合监测浮标",
                        "relation": "monitored_by",
                        "weight": 0.8,
                        "properties": {},
                    },
                    {
                        "source_ref": f"{center_name} 综合监测浮标",
                        "target_name": f"{center_name} 溶解氧观测",
                        "relation": "has_observation",
                        "weight": 0.75,
                        "properties": {},
                    },
                ],
                "summary": "补充了监测浮标和关键观测项。",
            }
        if expand_type == "ecological_species":
            return {
                "nodes": [
                    {
                        "type": "Species",
                        "name": "小黄鱼",
                        "properties": {"habitat": center_name, "sensitivity": "medium"},
                    },
                    {
                        "type": "FisheryArea",
                        "name": f"{center_name} 渔业适宜区",
                        "properties": {"suitability": 0.74},
                    },
                ],
                "edges": [
                    {
                        "source_ref": f"{center_name} 渔业适宜区",
                        "target_name": "小黄鱼",
                        "relation": "suitable_for",
                        "weight": 0.72,
                        "properties": {},
                    }
                ],
                "summary": "补充了生态物种和渔场适宜性关联。",
            }
        return {
            "nodes": [
                {
                    "type": "RedTideEvent",
                    "name": f"{center_name} 赤潮风险事件",
                    "properties": {"risk_level": "medium", "confidence": 0.7},
                }
            ],
            "edges": [
                {
                    "source_ref": context["current_node"]["id"],
                    "target_name": f"{center_name} 赤潮风险事件",
                    "relation": "has_risk_event",
                    "weight": 0.7,
                    "properties": {},
                }
            ],
            "summary": "补充了相关风险事件。",
        }

    def _mock_agent_answer(self, context: dict[str, Any]) -> str:
        agent_type = context["agent_type"]
        node_name = (context.get("node") or {}).get("name", "目标海域")
        answers = {
            "red_tide": f"根据当前模拟观测数据，{node_name} 叶绿素和营养盐信号偏高，赤潮风险为中等。",
            "current_analysis": f"{node_name} 当前海流整体稳定，局部流速变化需要继续跟踪。",
            "route_optimization": f"建议航线避开中等风险海域，并优先选择浮标覆盖较完整的航段。",
            "ecological_qa": f"结合图谱关系，{node_name} 的生态状态主要受水温、盐度和营养盐输入影响。",
            "buoy_diagnosis": "浮标状态总体在线，电量和最近上报时间未显示严重异常。",
            "fishery_assessment": f"{node_name} 渔业适宜性处于中等偏高水平，需关注赤潮风险对渔获的影响。",
        }
        return answers.get(agent_type, "已完成 mock 智能体分析。")

    def _mock_report(self, context: dict[str, Any]) -> str:
        title = context.get("title", "海洋分析报告")
        node_name = (context.get("node") or {}).get("name", "目标海域")
        return (
            f"# {title}\n\n"
            f"## 结论\n\n{node_name} 当前处于可观测、可分析状态，整体风险需要持续跟踪。\n\n"
            "## 数据依据\n\n- 图谱节点与一跳关系\n- 模拟海洋观测数据\n- 浮标状态与海流场数据\n\n"
            "## 建议\n\n1. 保持高频观测。\n2. 对中等以上风险信号触发复核。\n3. 将报告结果与图谱扩展结果联动归档。\n"
        )
