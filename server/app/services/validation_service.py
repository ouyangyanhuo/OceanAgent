"""候选数据校验服务。

LLM 不能直接决定最终图谱。它只能返回候选 nodes/edges，
本服务负责根据 schema_rules.json 检查候选结果是否可写入图谱。
"""

from typing import Any

from app.core.errors import ValidationError
from app.core.json_store import read_json
from app.core.paths import SCHEMA_RULES_FILE
from app.models.graph import GraphData


class ValidationService:
    """封装图谱扩展规则和候选结果校验。"""

    def load_schema_rules(self) -> dict[str, Any]:
        """读取 schema_rules.json。"""
        # schema_rules 是后端约束 LLM 输出的核心配置，文件缺失时返回空对象让调用方显式失败。
        return read_json(SCHEMA_RULES_FILE, {})

    def get_expand_rule(self, expand_type: str) -> dict[str, Any]:
        """获取指定扩展类型的规则。"""
        rules = self.load_schema_rules()

        # expand_types 下每个 key 对应一种扩展方向，例如 risk_factors、monitoring_buoys。
        expand_rules = rules.get("expand_types", {})
        if expand_type not in expand_rules:
            # 不允许 LLM 或前端自由创造扩展类型。
            raise ValidationError(f"Unsupported expand_type: {expand_type}", code="INVALID_EXPAND_TYPE")
        return expand_rules[expand_type]

    def validate_expansion_result(
        self,
        result: dict[str, Any],
        expand_type: str,
        graph: GraphData,
    ) -> dict[str, Any]:
        """校验 LLM 返回的扩展候选结果。

        这里不做 ID 生成和去重，只验证结构、类型、数量和字段合法性。
        通过校验后由 ExpansionService 写入正式图谱。
        """
        # 第一层校验返回值必须是 JSON object，不能是字符串、列表或 Markdown 文本。
        if not isinstance(result, dict):
            raise ValidationError("LLM result must be a JSON object")

        # nodes/edges 是后续写图流程的最低要求；summary 可以缺省。
        if "nodes" not in result or "edges" not in result:
            raise ValidationError("LLM result must contain nodes and edges")

        rule = self.get_expand_rule(expand_type)

        # 允许 nodes/edges 为空数组，但不允许字段类型不是数组。
        nodes = result.get("nodes") or []
        edges = result.get("edges") or []
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValidationError("nodes and edges must be arrays")

        # 数量上限来自 schema_rules，避免一次扩展把图谱膨胀得不可控。
        if len(nodes) > rule["max_nodes"]:
            raise ValidationError("Too many candidate nodes")
        if len(edges) > rule["max_edges"]:
            raise ValidationError("Too many candidate edges")

        existing_ids = {node.id for node in graph.nodes}

        # 校验候选节点：类型、名称、属性结构，以及不能覆盖已有 ID。
        for node in nodes:
            # 真实写入时 ID 由后端生成；如果 LLM 给了已存在 ID，直接拒绝。
            if "id" in node and node["id"] in existing_ids:
                raise ValidationError("LLM result must not override existing node IDs")

            # 节点类型必须被当前 expand_type 允许，而不只是全局允许。
            if node.get("type") not in rule["allowed_node_types"]:
                raise ValidationError(f"Invalid node type: {node.get('type')}")

            # 空 name 无法参与去重和 ID 生成。
            if not node.get("name"):
                raise ValidationError("Candidate node name cannot be empty")

            # properties 必须保持对象，避免写入字符串/数组导致前端处理分支复杂化。
            if not isinstance(node.get("properties", {}), dict):
                raise ValidationError("Candidate node properties must be an object")

        # 校验候选边：关系类型、权重范围和属性结构。
        for edge in edges:
            # 关系类型也必须被当前 expand_type 允许。
            if edge.get("relation") not in rule["allowed_relations"]:
                raise ValidationError(f"Invalid relation: {edge.get('relation')}")

            # weight 缺省按 1.0 处理，但如果提供了必须是 0 到 1 的数字。
            weight = edge.get("weight", 1.0)
            if not isinstance(weight, int | float) or weight < 0 or weight > 1:
                raise ValidationError("Edge weight must be between 0 and 1")

            # 边属性同样保持对象，便于后续补充 description、confidence 等结构化字段。
            if not isinstance(edge.get("properties", {}), dict):
                raise ValidationError("Candidate edge properties must be an object")

        # 返回原对象，方便调用方继续使用 summary 等额外字段。
        return result
