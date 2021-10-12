from __future__ import annotations

from .types.enum import NotificationType
from .decorators import auth_required
from .types.rdict import RDict
from .model import Model

import logging
import time

class Notification(Model):
    __slots__ = (
        "created_at", "details", "id", "message", "seen",
        "sender_user_id", "sender_username", "type"
    )

    __types__ = RDict({
        "created_at": time.struct_time,
        "details": str,
        "id": str,
        "message": str,
        "seen": bool,
        "sender_user_id": str,
        "sender_username": str,
        "type": NotificationType
    })

    @auth_required
    async def accept_friend_request(self):
        """Accepts this friend request - if it is one"""
        if self.type != NotificationType.FRIEND_REQUEST:
            raise TypeError("Can not accept friend request from notification of type %s" % self.type)

        await self.client.request.put(
            "/auth/user/notifications/%s/accept" % self.id)

    async def mark_as_read(self) -> Notification:
        """Marks this notification as seen"""
        resp = await self.client.mark_notification_as_read(self.id)
        return resp

    async def delete(self) -> Notification:
        """Deletes this notification"""
        resp = await self.client.delete_notification(self.id)
        return resp