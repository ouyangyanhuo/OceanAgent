"""通知 API。"""

from fastapi import APIRouter

from app.core.response import success
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notification", tags=["notification"])
notification_service = NotificationService()


@router.get("")
def get_notifications() -> dict:
    """获取全部通知。"""
    result = notification_service.get_notifications()
    return success(result.model_dump(mode="json"))


@router.get("/unread-count")
def get_unread_count() -> dict:
    """获取未读通知数量。"""
    count = notification_service.get_unread_count()
    return success({"unread_count": count})


@router.post("/{notification_id}/read")
def mark_read(notification_id: str) -> dict:
    """标记单条通知为已读。"""
    found = notification_service.mark_read(notification_id)
    return success({"found": found})


@router.post("/read-all")
def mark_all_read() -> dict:
    """标记全部通知为已读。"""
    notification_service.mark_all_read()
    return success({"ok": True})
