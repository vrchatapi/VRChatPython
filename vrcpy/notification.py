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

class FriendRequestNotification(BaseNotification):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop)

        # TODO: Finish this object

        self._assign(obj)
