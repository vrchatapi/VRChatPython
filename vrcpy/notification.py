from .types.enum import NotificationType
from .model import Model

import time

class Notification(Model):
    __slots__ = (
        "created_at", "details", "id", "message", "seen",
        "sender_user_id", "sender_username", "type"
    )

    __types__ = {
        "created_at": time.struct_time,
        "details": str,
        "id": str,
        "message": str,
        "seen": bool,
        "sender_user_id": str,
        "sender_username": str,
        "type": NotificationType
    }