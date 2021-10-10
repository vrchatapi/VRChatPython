from __future__ import annotations

from .types.enum import NotificationType
from .decorators import auth_required
from .model import Model

import logging
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

    @auth_required
    async def accept_friend_request(self):
        if self.type != NotificationType.FRIEND_REQUEST:
            raise TypeError("Can not accept friend request from notification of type %s" % self.type)

        await self.client.request.put(
            "/auth/user/notifications/%s/accept" % self.id)

    @auth_required
    async def mark_as_read(self) -> Notification:
        logging.debug("Marking notification as read %s" % self.id)

        resp = await self.client.request.put(
            "/auth/user/notifications/%s/see" % self.id)
        return Notification(self.client, resp["data"])

    @auth_required
    async def delete(self) -> Notification:
        logging.debug("Deleting notification %s" % self.id)

        resp = await self.client.request.put(
            "/auth/user/notifications/%s/hide" % self.id)
        return Notification(self.client, resp["data"])