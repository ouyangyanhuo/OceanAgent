from typing import Any

from app.core.errors import ValidationError
from app.core.json_store import read_json
from app.core.paths import SCHEMA_RULES_FILE
from app.models.graph import GraphData


class ValidationService:
    def load_schema_rules(self) -> dict[str, Any]:
        return read_json(SCHEMA_RULES_FILE, {})

    def get_expand_rule(self, expand_type: str) -> dict[str, Any]:
        rules = self.load_schema_rules()
        expand_rules = rules.get("expand_types", {})
        if expand_type not in expand_rules:
            raise ValidationError(f"Unsupported expand_type: {expand_type}", code="INVALID_EXPAND_TYPE")
        return expand_rules[expand_type]

    def validate_expansion_result(
        self,
        result: dict[str, Any],
        expand_type: str,
        graph: GraphData,
    ) -> dict[str, Any]:
        if not isinstance(result, dict):
            raise ValidationError("LLM result must be a JSON object")
        if "nodes" not in result or "edges" not in result:
            raise ValidationError("LLM result must contain nodes and edges")

        rule = self.get_expand_rule(expand_type)
        nodes = result.get("nodes") or []
        edges = result.get("edges") or []
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValidationError("nodes and edges must be arrays")
        if len(nodes) > rule["max_nodes"]:
            raise ValidationError("Too many candidate nodes")
        if len(edges) > rule["max_edges"]:
            raise ValidationError("Too many candidate edges")

        existing_ids = {node.id for node in graph.nodes}
        for node in nodes:
            if "id" in node and node["id"] in existing_ids:
                raise ValidationError("LLM result must not override existing node IDs")
            if node.get("type") not in rule["allowed_node_types"]:
                raise ValidationError(f"Invalid node type: {node.get('type')}")
            if not node.get("name"):
                raise ValidationError("Candidate node name cannot be empty")
            if not isinstance(node.get("properties", {}), dict):
                raise ValidationError("Candidate node properties must be an object")

        for edge in edges:
            if edge.get("relation") not in rule["allowed_relations"]:
                raise ValidationError(f"Invalid relation: {edge.get('relation')}")
            weight = edge.get("weight", 1.0)
            if not isinstance(weight, int | float) or weight < 0 or weight > 1:
                raise ValidationError("Edge weight must be between 0 and 1")
            if not isinstance(edge.get("properties", {}), dict):
                raise ValidationError("Candidate edge properties must be an object")

        return result
