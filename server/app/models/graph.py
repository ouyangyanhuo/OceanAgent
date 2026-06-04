"""图谱相关 Pydantic 模型。

这些模型对应 app/data/graph/graph.json 的节点、边和图谱整体结构，
也是图谱接口和扩展接口的核心数据类型。
"""

from typing import Any

from pydantic import BaseModel, Field


class GraphMetadata(BaseModel):
    """节点和边的元数据。

    locked 表示结构层默认稳定，不应被 LLM 随意覆盖。
    parent_node 用于记录扩展来源，便于追踪某个节点或边由哪个中心节点生成。
    """

    source: str = "manual"
    parent_node: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    version: int = 1
    locked: bool = True


class GraphNode(BaseModel):
    """图谱节点。

    type 必须来自 schema_rules.json 的 allowed_node_types。
    properties 保存领域属性，expanded 记录该节点每个 expand_type 是否已经扩展过。
    """

    id: str
    type: str
    name: str
    properties: dict[str, Any] = Field(default_factory=dict)
    expanded: dict[str, bool] = Field(default_factory=dict)
    metadata: GraphMetadata = Field(default_factory=GraphMetadata)


class GraphEdge(BaseModel):
    """图谱边。

    source/target 保存节点 ID，relation 必须来自 schema_rules.json 的 allowed_relations。
    weight 表示关系强度或置信度，第一版约定范围为 0 到 1。
    """

    id: str
    source: str
    target: str
    relation: str
    weight: float = 1.0
    properties: dict[str, Any] = Field(default_factory=dict)
    metadata: GraphMetadata = Field(default_factory=GraphMetadata)


class GraphData(BaseModel):
    """完整图谱文件结构。"""

    graph_id: str
    version: int = 1
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class ExpandNodeRequest(BaseModel):
    """节点扩展请求。"""

    node_id: str
    expand_type: str
    force_refresh: bool = False


class ExpandNodeResponse(BaseModel):
    """节点扩展响应。

    from_cache=True 表示命中 expansion_index.json，未再次生成结构。
    """

    center_node: GraphNode
    new_nodes: list[GraphNode] = Field(default_factory=list)
    new_edges: list[GraphEdge] = Field(default_factory=list)
    from_cache: bool = False
    summary: str | None = None


class CreateSeedNodeRequest(BaseModel):
    """新建种子节点请求。"""

    description: str


class CreateSeedNodeResponse(BaseModel):
    """新建种子节点响应。"""

    seed_node: GraphNode
    new_nodes: list[GraphNode] = Field(default_factory=list)
    new_edges: list[GraphEdge] = Field(default_factory=list)
    summary: str | None = None


class ConnectNodesRequest(BaseModel):
    """节点连接请求。"""

    source_node_id: str
    target_node_id: str


class ConnectNodesResponse(BaseModel):
    """节点连接响应。"""

    source_node: GraphNode
    target_node: GraphNode
    bridge_node: GraphNode
    new_edges: list[GraphEdge] = Field(default_factory=list)
    summary: str | None = None
