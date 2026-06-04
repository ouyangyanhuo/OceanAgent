"""通知服务。

管理通知的创建、查询和已读状态。
通知最多保留 MAX_NOTIFICATIONS 条，超出时自动淘汰最旧的。
"""

from __future__ import annotations

import uuid

from app.core.json_store import read_json, write_json
from app.core.paths import NOTIFICATION_FILE
from app.models.notification import Notification, NotificationList

MAX_NOTIFICATIONS = 5


class NotificationService:
    """通知 CRUD 服务。"""

    def _load(self) -> NotificationList:
        data = read_json(NOTIFICATION_FILE, {"notifications": [], "unread_count": 0})
        return NotificationList(**data)

    def _save(self, nl: NotificationList) -> None:
        write_json(NOTIFICATION_FILE, nl.model_dump(mode="json"))

    def get_notifications(self) -> NotificationList:
        """返回全部通知。"""
        return self._load()

    def get_unread_count(self) -> int:
        """返回未读数量。"""
        return self._load().unread_count

    def create_notification(
        self,
        title: str,
        message: str,
        notification_type: str = "graph_expansion",
        related_node_id: str | None = None,
    ) -> Notification:
        """创建一条通知，超过上限时淘汰最旧的。"""
        nl = self._load()

        notif = Notification(
            id=uuid.uuid4().hex[:12],
            type=notification_type,
            title=title,
            message=message,
            related_node_id=related_node_id,
        )

        nl.notifications.insert(0, notif)

        # 超过上限时淘汰最旧的
        if len(nl.notifications) > MAX_NOTIFICATIONS:
            nl.notifications = nl.notifications[:MAX_NOTIFICATIONS]

        nl.unread_count = sum(1 for n in nl.notifications if not n.read)
        self._save(nl)
        return notif

    def mark_read(self, notification_id: str) -> bool:
        """标记单条通知为已读。返回是否找到。"""
        nl = self._load()
        for n in nl.notifications:
            if n.id == notification_id:
                n.read = True
                nl.unread_count = sum(1 for x in nl.notifications if not x.read)
                self._save(nl)
                return True
        return False

    def mark_all_read(self) -> None:
        """标记全部通知为已读。"""
        nl = self._load()
        for n in nl.notifications:
            n.read = True
        nl.unread_count = 0
        self._save(nl)
