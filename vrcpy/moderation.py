from vrcpy.baseobject import BaseObject
import logging


class PlayerModeration(BaseObject):
    """Base moderation class that all moderations inherit from"""

    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop)

        self.required.update({
            "created_at": {
                "dict_key": "created",
                "type": str
            },
            "id": {
                "dict_key": "id",
                "type": str
            },
            "source_display_name": {
                "dict_key": "sourceDisplayName",
                "type": str
            },
            "source_user_id": {
                "dict_key": "sourceUserId",
                "type": str
            },
            "target_display_name": {
                "dict_key": "targetDisplayName",
                "type": str
            },
            "target_user_id": {
                "dict_key": "targetUserId",
                "type": str
            },
            "type": {
                "dict_key": "type",
                "type": str
            }
        })

        self._assign(obj)

    async def fetch_source_user(self):
        """Fetches the user that created the moderation"""

        user = await self.client.fetch_user(self.source_user_id)
        return user

    async def fetch_target_user(self):
        "Fetches the user that the moderation was applied on"""

        user = await self.client.fetch_user(self.target_user_id)
        return user

    async def clear_moderation(self):
        """Unapplies this moderation from the targeted user"""

        await self.client.request.delete(
            "/user/%s/moderations/%s" % (
                self.source_user_id, self.target_user_id))
        logging.debug("Cleared moderations for " + self.source_user_id)

    @staticmethod
    def build_moderation(client, obj, loop=None):
        ## TODO: camelCase
        switch = {
            "block": BlockPlayerModeration,
            "showAvatar": ShowAvatarModeration,
            "hideAvatar": HideAvatarModeration,
            "mute": MutePlayerModeration,
            "unmute": UnmutePlayerModeration
        }

        if obj["type"] in switch:
            return switch[obj["type"]](client, obj, loop)

        return PlayerModeration(client, obj, loop)

    @staticmethod
    async def create_moderation(self, t, user_id, client):
        """
        Applies a moderation against a user

        Arguments
        ----------
        t: :class:`str`
            Type of moderation to create:
                moderations = ["block", "showAvatar", "hideAvatar", "mute", "unmute"]
        user_id: :class:`str`
            ID of VRChat user to apply moderation to
        client: :class:`vrcpy.Client`
            Current logged in client
        """

        if t == "block":
            mod = await client.request.post(
                "/auth/user/blocks",
                params={"blocked": user_id})

            return BlockPlayerModeration(client, mod["data"], client.loop)

        mod = await client.request.post(
            "/auth/user/playermoderations", params={
                "type": t, "moderated": user_id})

        return PlayerModeration.build_moderation(client, mod["data"], client.loop)


class BlockPlayerModeration(PlayerModeration):
    """Represents a user-block moderation"""

    async def unblock(self):
        """Unblocks the target user/Clears block moderation from target user"""

        await self.client.request.put(
            "/auth/user/unblocks", params={
                "blocked": self.target_user_id})

        logging.debug("Unblocked user %s" % self.target_user_id)


class ShowAvatarModeration(PlayerModeration):
    """Represents a show-user-avatar moderation"""
    pass


class HideAvatarModeration(PlayerModeration):
    """Represents a hide-user-avatar moderation"""
    pass


class MutePlayerModeration(PlayerModeration):
    """Represents a mute-user moderation"""
    pass


class UnmutePlayerModeration(PlayerModeration):
    """Represents an unmute-user moderation"""
    pass


# Don't know if these still exist but including them just incase

class Moderation(BaseObject):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop)

        self.required.update({
            "created_at": {
                "dict_key": "created",
                "type": str
            },
            "reason": {
                "dict_key": "reason",
                "type": str
            },
            "world_id": {
                "dict_key": "worldId",
                "type": str
            },
            "instance_id": {
                "dict_key": "instanceId",
                "type": str
            },
            "type": {
                "dict_key": "type",
                "type": str
            }
        })

        self._assign(obj)

    async def fetch_instance(self):
        instance = await self.client.fetch_instance(
            self.world_id, self.instance_id)
        return instance

    @staticmethod
    def build_moderation(self, client, obj, loop=None):
        switch = {
            "warn": WarnModeration,
            "kick": KickModeration,
            "ban": BanModeration
        }

        if obj["type"] in switch:
            return switch[obj["type"]](client, obj, loop)

        return Moderation(client, obj, loop)


class WarnModeration(Moderation):
    pass


class KickModeration(Moderation):
    pass


class BanModeration(Moderation):
    pass
