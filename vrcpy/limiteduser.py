from .types.enum import PlayerModerationType
from .notification import Notification
from .decorators import auth_required
from .moderation import Moderation
from .model import Model

from typing import Dict

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

    @auth_required
    async def unfriend(self):
        logging.debug("Unfriending %s" % self.id)

        if not self.is_friend:
            raise TypeError("Can't unfriend a user that isn't a friend")

        await self.client.request.delete("/auth/user/friends/%s" % self.id)

    @auth_required
    async def friend(self) -> Notification:
        logging.debug("Friending %s" % self.id)

        if self.is_friend:
            raise TypeError("Can't friend user that is already a friend")

        resp = await self.client.request.post(
            "/auth/%s/friendRequest" % self.id)
        return Notification(self.client, resp["data"])

    @auth_required
    async def cancel_friend(self):
        logging.debug("Cancelling friend request to %s" % self.id)

        await self.client.request.delete(
            "/user/%s/friendRequest" % self.id)

    @auth_request
    async def fetch_friend_status(self) -> Dict[str, bool]:
        logging.debug("Fetching friend status for %s" % self.id)

        resp = await self.client.request.get("/user/%s/friendStatus" % self.id)
        resp = {
            "incoming_request": resp["data"]["incomingRequest"],
            "is_friend": resp["data"]["isFriend"],
            "outgoing_request": resp["data"]["outgoingRequest"]
        }

        return resp