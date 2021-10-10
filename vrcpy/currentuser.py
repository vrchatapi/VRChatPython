from .decorators import auth_required
from .limiteduser import LimitedUser
from .moderation import Moderation
from .user import User

from .types.enum import UserStatus, PlayerModerationType

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