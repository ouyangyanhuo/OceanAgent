from typing import Any

from pydantic import BaseModel, Field


class GraphMetadata(BaseModel):
    source: str = "manual"
    parent_node: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    version: int = 1
    locked: bool = True


class GraphNode(BaseModel):
    id: str
    type: str
    name: str
    properties: dict[str, Any] = Field(default_factory=dict)
    expanded: dict[str, bool] = Field(default_factory=dict)
    metadata: GraphMetadata = Field(default_factory=GraphMetadata)


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relation: str
    weight: float = 1.0
    properties: dict[str, Any] = Field(default_factory=dict)
    metadata: GraphMetadata = Field(default_factory=GraphMetadata)


class GraphData(BaseModel):
    graph_id: str
    version: int = 1
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class ExpandNodeRequest(BaseModel):
    node_id: str
    expand_type: str
    force_refresh: bool = False


class ExpandNodeResponse(BaseModel):
    center_node: GraphNode
    new_nodes: list[GraphNode] = Field(default_factory=list)
    new_edges: list[GraphEdge] = Field(default_factory=list)
    from_cache: bool = False
    summary: str | None = None
