from .types.enum import PlayerModerationType
from .decorators import auth_required
from .moderation import Moderation
from .model import Model

class LimitedUser(Model):
    __slots__ = (
        "bio", "current_avatar_image_url",
        "current_avatar_thumbnail_image_url", "developer_type",
        "display_name", "fallback_avatar", "id", "is_friend", "last_platform",
        "profile_pic_override", "status", "status_description", "tags",
        "user_icon", "username"
    )

    @auth_required
    async def moderate(self, typeof: PlayerModerationType) -> Moderation:
        logging.debug("Creating %s moderation on %s" % (
            typeof.value, self.id))

        resp = await self.client.request.post(
            "/auth/user/playermoderations",
            params={"moderated": self.id, "type": typeof})
        return Moderation(self.client, resp["data"])

    @auth_required
    async def unmoderate(self, typeof: PlayerModerationType):
        logging.debug("Removing %s moderation on %s" % (
            typeof.value, self.id))

        await self.client.request.put(
            "/auth/user/unplayermoderate",
            params={"moderated": self.id, "type": typeof})