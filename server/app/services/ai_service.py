"""AI 服务封装。

第一版保持 mock 模式，确保没有 API Key 时系统也能完整跑通。
未来接 OpenAI 或自定义 LLM 时，应在这里新增 provider 分支，
不要让 API 路由或业务服务直接调用外部模型。
"""

from typing import Any


class AIService:
    """统一封装图谱扩展、智能体回答和报告生成。"""

    def generate_graph_seed(self, topic: str) -> dict[str, Any]:
        """生成种子图谱候选数据。

        当前返回 mock 候选结构；后续真实 LLM 输出也必须保持候选数据格式。
        """
        return {
            # 候选节点不包含 id；后端会在 GraphService.build_node 中统一生成。
            "nodes": [
                {
                    "type": "SeaArea",
                    "name": topic,
                    "properties": {"description": f"{topic} 的种子海域节点。"},
                }
            ],
            # 种子图可以没有边，后续脚本或扩展流程再补充关系。
            "edges": [],
            "summary": "已生成 mock 种子图谱候选数据。",
        }

    def generate_graph_expansion(self, context: dict[str, Any]) -> dict[str, Any]:
        """生成图谱扩展候选节点和候选边。"""
        # 后续真实 LLM provider 可在这里接入；v1 始终保持 mock 可运行。
        return self._mock_graph_expansion(context)

    def generate_agent_answer(self, context: dict[str, Any]) -> str:
        """生成智能体回答文本。"""
        return self._mock_agent_answer(context)

    def generate_report(self, context: dict[str, Any]) -> str:
        """生成 Markdown 报告文本。"""
        return self._mock_report(context)

    def _mock_graph_expansion(self, context: dict[str, Any]) -> dict[str, Any]:
        """根据 expand_type 返回稳定的 mock 图谱扩展候选结果。"""
        # expand_type 决定生成哪类候选结构；当前值来自 schema_rules 校验后的请求。
        expand_type = context["expand_type"]

        # 中心节点名称用于生成更贴近上下文的 mock 名称和描述。
        center_name = context["current_node"]["name"]
        if expand_type == "risk_factors":
            # 赤潮风险因子扩展：生成风险因子和治理措施。
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
                        # source_ref 可以直接使用中心节点 ID，ExpansionService 会映射为正式 source。
                        "source_ref": context["current_node"]["id"],
                        "target_name": "叶绿素浓度升高",
                        "relation": "affected_by",
                        "weight": 0.84,
                        "properties": {"description": f"{center_name} 受到叶绿素浓度升高影响。"},
                    },
                    {
                        # 这里用中文节点名作为 source_ref，模拟 LLM 常见的“按名称引用本次节点”输出。
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
            # 监测浮标扩展：生成浮标和观测记录。
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
            # 生态物种扩展：生成物种和渔业适宜区。
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
        # 默认分支覆盖 related_events 等风险事件类扩展。
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
        """根据 agent_type 返回稳定的 mock 智能体回答。"""
        agent_type = context["agent_type"]

        # 没有绑定节点时使用“目标海域”兜底，保证回答文本总是完整。
        node_name = (context.get("node") or {}).get("name", "目标海域")

        # 每个 agent_type 固定一条领域化 mock 回答，便于前端调试不同页面。
        answers = {
            "red_tide": f"根据当前模拟观测数据，{node_name} 叶绿素和营养盐信号偏高，赤潮风险为中等。",
            "current_analysis": f"{node_name} 当前海流整体稳定，局部流速变化需要继续跟踪。",
            "route_optimization": f"建议航线避开中等风险海域，并优先选择浮标覆盖较完整的航段。",
            "ecological_qa": f"结合图谱关系，{node_name} 的生态状态主要受水温、盐度和营养盐输入影响。",
            "buoy_diagnosis": "浮标状态总体在线，电量和最近上报时间未显示严重异常。",
            "fishery_assessment": f"{node_name} 渔业适宜性处于中等偏高水平，需关注赤潮风险对渔获的影响。",
        }

        # 理论上 agent_type 已在 AgentService 校验；这里保留兜底，避免直接调用时报错。
        return answers.get(agent_type, "已完成 mock 智能体分析。")

    def _mock_report(self, context: dict[str, Any]) -> str:
        """返回稳定的 Markdown mock 报告。"""
        # 标题由 ReportService 传入；缺省值用于直接调用 AIService 的兜底。
        title = context.get("title", "海洋分析报告")

        # 报告正文尽量围绕节点名称；没有节点时使用通用称呼。
        node_name = (context.get("node") or {}).get("name", "目标海域")
        return (
            f"# {title}\n\n"
            f"## 结论\n\n{node_name} 当前处于可观测、可分析状态，整体风险需要持续跟踪。\n\n"
            "## 数据依据\n\n- 图谱节点与一跳关系\n- 模拟海洋观测数据\n- 浮标状态与海流场数据\n\n"
            "## 建议\n\n1. 保持高频观测。\n2. 对中等以上风险信号触发复核。\n3. 将报告结果与图谱扩展结果联动归档。\n"
        )
