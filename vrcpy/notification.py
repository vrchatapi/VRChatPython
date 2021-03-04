from vrcpy.baseobject import BaseObject
import logging


class Notification:
    class Type:
        # Sendable

        request_invite = "requestInvite"
        invite = "invite"

        # Receivable

        all = "all"
        friend_request = "friendRequest"


class BaseNotification(BaseObject):
    def __init__(self, client, loop=None):
        super().__init__(client, loop)

        self.required.update({
            "id": {
                "dict_key": "id",
                "type": str
            },
            "sender_username": {
                "dict_key": "senderUsername",
                "type": str
            },
            "sender_user_id": {
                "dict_key": "sendUserId",
                "type": str
            },
            "type": {
                "dict_key": "type",
                "type": str
            },
            "created_at": {
                "dict_key": "created_at",
                "type": str
            }
        })

        self.optional.update({
            "details": {
                "dict_key": "details",
                "type": dict
            },
            "message": {
                "dict_key": "message",
                "type": str
            },
            "seen": {
                "dict_key": "seen",
                "type": bool
            }
        })

        self.detail_required = {}

    def _assign(self, obj):
        super()._assign(obj)

        if "details" in obj and obj["details"] is not None:
            self.required = self.detail_required
            self.optional = {}

            super()._assign(obj["details"])

        del self.detail_required

    @staticmethod
    def build_notification(client, obj, loop=None):
        switch = {
            "invite": InviteNotification,
            "requestInvite": RequestInviteNotification,
            "requestInviteResponse": RequestInviteResponseNotification,
            "friendRequest": FriendRequestNotification
        }

        logging.debug("Building notification of type " + obj["type"])
        return switch[obj["type"]](client, obj, loop)

    async def mark_seen(self):
        '''
        Tells VRC that this notification has been seen
        Returns updated class of this notification
        '''

        notif = await self.client.request.call(
            "/auth/user/notifications/%s/see" % self.id,
            "PUT", params={"notificationId": self.id})
        return self.__class__(self.client, notif["data"], self.loop)

    async def hide(self):
        '''
        Tells VRC not to show this notification as new
        Returns updated class of this notification
        '''

        notif = await self.client.request.call(
            "/auth/user/notifications/%s/hide" % self.id,
            "PUT", params={"notificationId": self.id})
        return self.__class__(self.client, notif["data"], self.loop)


class InviteNotification(BaseNotification):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop)

        self.detail_required.update({
            "world_id": {
                "dict_key": "worldId",
                "type": str
            }
        })

        self._assign(obj)


class RequestInviteNotification(BaseNotification):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop)

        self.detail_required.update({
            "platform": {
                "dict_key": "platform",
                "type": str
            }
        })

        self._assign(obj)


class RequestInviteResponseNotification(BaseNotification):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop)

        self.detail_required.update({
            "in_response_to": {
                "dict_key": "inResponseTo",
                "type": str
            },
            "response_message": {
                "dict_key": "responseMessage",
                "type": str
            }
        })


class FriendRequestNotification(BaseNotification):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop)

        # TODO: Finish this object

        self._assign(obj)
