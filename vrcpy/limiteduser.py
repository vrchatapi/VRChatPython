from .types.enum import PlayerModerationType
from .favoritegroup import FavoriteGroup
from .notification import Notification
from .decorators import auth_required
from .moderation import Moderation
from .model import Model

from typing import Dict, List
import logging

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
        """
        Adds a :class:`PlayerModeration` moderation to this user

        Arguments
        ----------
        typeof: :class:`PlayerModerationType`
            Type of moderation to add
        """

        logging.debug("Creating %s moderation on %s" % (
            typeof.value, self.id))

        resp = await self.client.request.post(
            "/auth/user/playermoderations",
            params={"moderated": self.id, "type": typeof})
        return Moderation(self.client, resp["data"])

    @auth_required
    async def unmoderate(self, typeof: PlayerModerationType):
        """
        Removes a :class:`PlayerModerationType` moderation from this user

        Arguments
        ----------
        typeof: :class:`PlayerModerationType`
            Type of moderation to remove
        """
        logging.debug("Removing %s moderation on %s" % (
            typeof.value, self.id))

        await self.client.request.put(
            "/auth/user/unplayermoderate",
            params={"moderated": self.id, "type": typeof})

    @auth_required
    async def unfriend(self):
        """Unfriends this user"""
        logging.debug("Unfriending %s" % self.id)

        if not self.is_friend:
            raise TypeError("Can't unfriend a user that isn't a friend")

        await self.client.request.delete("/auth/user/friends/%s" % self.id)

    @auth_required
    async def friend(self) -> Notification:
        """Sends a :class:`PlayerModerationType.FRIEND_REQUEST` notification to this user"""
        logging.debug("Friending %s" % self.id)

        if self.is_friend:
            raise TypeError("Can't friend user that is already a friend")

        resp = await self.client.request.post(
            "/auth/%s/friendRequest" % self.id)
        return Notification(self.client, resp["data"])

    @auth_required
    async def cancel_friend(self):
        """Cancels a :class:`PlayerModerationType.FRIEND_REQUEST` notification that was sent to this user"""
        logging.debug("Cancelling friend request to %s" % self.id)

        await self.client.request.delete(
            "/user/%s/friendRequest" % self.id)

    @auth_required
    async def fetch_friend_status(self) -> Dict[str, bool]:
        """Gets the friend status of this user"""
        logging.debug("Fetching friend status for %s" % self.id)

        resp = await self.client.request.get("/user/%s/friendStatus" % self.id)
        resp = {
            "incoming_request": resp["data"]["incomingRequest"],
            "is_friend": resp["data"]["isFriend"],
            "outgoing_request": resp["data"]["outgoingRequest"]
        }

        return resp

    @auth_required
    async def fetch_favorite_groups(
        self, n: int = 60, offset: int = 0) -> List[FavoriteGroup]:
        """
        Fetches a list of favorite groups owned by a user

        Keyword Arguments
        ------------------
        n: :class:`int`
            Number of :class:`vrcpy.favoritegroup.FavoriteGroup` to return
        offset: :class:`int`
            Zero-based offset from start of object return\n
            Used for pagination
        """
        req = {}
        names = {
            "n": n,
            "offset": offset,
            "ownerId": self.id
        }

        for attr in names:
            if names[attr] is not None:
                req[attr] = names[attr]

        logging.debug("Listing favorite groups %s" % req)
        resp = await self.client.request.get("/favorite/groups", params=req)
        return [FavoriteGroup.favorite_group(self.client, group) for group in resp["data"]]