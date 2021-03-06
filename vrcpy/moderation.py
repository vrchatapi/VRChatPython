from vrcpy.baseobject import BaseObject
import logging


class PlayerModeration(BaseObject):
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
        '''
        returns source User object
        '''

        user = await self.client.fetch_user(self.source_user_id)
        return user

    async def fetch_target_user(self):
        '''
        returns target User object
        '''

        user = await self.client.fetch_user(self.target_user_id)
        return user

    async def clear_moderation(self):
        '''
        Clears this moderation from target player
        '''

        await self.client.request.call(
            "/user/%s/moderations/%s" % (
                self.source_user_id, self.target_user_id),
            "DELETE"
        )
        logging.debug("Cleared moderations for " + self.source_user_id)

    @staticmethod
    def build_moderation(client, obj, loop=None):
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
    async def create_moderation(self, t, user_id, client, loop=None):
        if t == "block":
            mod = await client.request.call(
                "/auth/user/blocks", "POST",
                params={"blocked": user_id})

            return BlockPlayerModeration(client, mod["data"], loop)

        mod = await client.request.call(
            "/auth/user/playermoderations", "POST", params={
                "type": t, "moderated": user_id})

        return PlayerModeration.build_moderation(client, mod["data"], loop)


class BlockPlayerModeration(PlayerModeration):
    async def unblock(self):
        await self.client.request.call(
            "/auth/user/unblocks", "PUT", params={
                "blocked": self.target_user_id})

        logging.debug("Unblocked user %s" % self.target_user_id)


class ShowAvatarModeration(PlayerModeration):
    pass


class HideAvatarModeration(PlayerModeration):
    pass


class MutePlayerModeration(PlayerModeration):
    pass


class UnmutePlayerModeration(PlayerModeration):
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
