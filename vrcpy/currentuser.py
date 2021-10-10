from .notification import Notification
from .decorators import auth_required
from .limiteduser import LimitedUser
from .moderation import Moderation
from .user import User

from .types.enum import UserStatus, PlayerModerationType
from .types.enum import NotificationType, SearchGenericType

import logging

from typing import List

class CurrentUser(User):
    @auth_required
    async def fetch_friends(
        self, offset: int = 0, n: int = 60, 
        offline: bool = False) -> List[LimitedUser]:

        logging.debug("Fetching friend list (offset=%s n=%s offline=%s)" % (
            offset, n, offline))

        friends = await self.client.request.get("/auth/user/friends")
        friends = [LimitedUser(
            self.client, user) for user in friends[data]]

        return friends

    @auth_required
    async def fetch_player_moderations(
        self, id: str, typeof: PlayerModerationType) -> List[Moderation]:
        logging.debug("Fetching player moderations")

        resp = self.client.request.get(
            "/auth/user/playermoderations",
            params={"targetUserId": id, "type": typeof.value})

    @auth_required
    async def fetch_moderation(
        self, id: str) -> Moderation:
        logging.debug("Fetching moderation %s" % id)

        resp = self.client.request.get("/auth/user/playermoderations/"+id)
        return Moderation(self.client, resp["data"])

    @auth_required
    async def clear_player_moderations(self):
        logging.debug("Clearing all moderations")

        await self.client.request.delete("/auth/user/playmoderations")

    @auth_required
    async def fetch_notifications(
        self, typeof: Union[
            NotificationType, SearchGenericType] = SearchGenericType.ALL,
        hidden: bool = False, after: str = None,
        n: int = 60, offset: int = 0) -> List[Notification]:

        if hidden and typeof != NotificationType.FRIEND_REQUEST:
            raise TypeError("Hidden can be True only when typeof kwarg is set to NotificationType.FRIEND_REQUEST")

        typeof = typeof.value
        params = {}
        names = {
            "type": typeof,
            "hidden": hidden,
            "after": after,
            "n": n,
            "offset": offset
        }
        
        for param in names:
            if names[param] is not None:
                params[param] = names[param]

        resp = await self.client.request.get("/auth/user/notifications",
                                             params=params)
        return [Notification(self.client, notif) for notif in resp["data"]]

    @auth_required
    async def clear_notifications(self):
        logging.debug("Clearing all notifications")

        await self.client.request.put("/auth/user/notifications/clear")

    @auth_required
    async def update(
        self, email: str = None, birthday: str = None,
        accepted_tos_version: int = None, tags: List[str] = None,
        status: UserStatus = None, status_description: str = None,
        bio: str = None, bio_links: List[str] = None,
        user_icon: str = None) -> CurrentUser:

        names = {
            "email": email,
            "birthday": birthday,
            "acceptedTOSVersion": accepted_tos_version,
            "tags": tags,
            "status": status.value,
            "statusDescription": status_description,
            "bio": bio,
            "bioLinks": bio_links,
            "userIcon": user_icon
        }

        req = {}

        for attr in names:
            if names[attr] is not None:
                req[attr] = names[attr]

        resp = self.client.request.put("/users/%s" % self.id, json=req)
        return CurrentUser(self.client, resp["data"])

    @auth_required
    async def delete_account(self) -> CurrentUser:
        logging.debug("Deleting user %s" % self.id)

        resp = await self.client.request.put("/user/%s/delete" % self.id)
        self.client.me = CurrentUser(self.client, resp["data"])

        return self.client.me