"""通知模型。"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Notification(BaseModel):
    """单条通知。"""

    id: str
    type: str = "graph_expansion"
    title: str
    message: str
    read: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    related_node_id: Optional[str] = None


class NotificationList(BaseModel):
    """通知列表，持久化到 notifications.json。"""

    notifications: list[Notification] = []
    unread_count: int = 0
