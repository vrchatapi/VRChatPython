from __future__ import annotations

from .types.enum import FavoriteType, Visibility
from .decorators import auth_required
from .model import Model

from typing import List
import logging

class FavoriteGroup(Model):
    __types__ = {
        "type": FavoriteType,
        "visibility": Visibility
    }

    @staticmethod
    def favorite_group(client, data):
        groups = {
            "world": FavoriteWorldGroup,
            "friend": FavoriteFriendGroup,
            "avatar": FavoriteAvatarGroup
        }

        return groups[data["type"]](client, data)

    @auth_required
    async def update(
        self, display_name: str = None, visibility: Visibility = None,
        tags: List[str] = None) -> FavoriteGroup:
        """
        Updates the favorite group

        Keyword Arguments
        ------------------
        display_name: :class:`str`
            New display name for the group
        visibility: :class:`vrcpy.types.enum.Visibility`
            New visibility for the group
        tags: :class:`list`[:class:`str`]
            New tags for the group
        """
        logging.debug(
            "Updating favorite group %s {%s: %s, %s: %s, %s: %s}" % (
                self.id, "display_name", display_name, "visibility",
                visibility, "tags", tags))

        req = {}
        names = {
            "displayName": display_name,
            "visibility": None if visibility is None else visibility.value,
            "tags": tags
        }
        
        for attr in names:
            if names[attr] is not None:
                req[attr] = names[attr]

        resp = await self.client.request.put(
            "/favorite/group/%s/%s/%s" % (
                self.type.value, self.name, self.owner_id), json=req)
        return FavoriteGroup(self.client, resp["data"])

    @auth_required
    async def clear(self):
        """Clears all favorites from this group"""
        logging.debug("Clearing favorite group %s" % self.id)

        await self.client.request.delete("/favorite/group/%s/%s/%s" % (
            self.type.value, self.name, self.owner_id))

class FavoriteWorldGroup(FavoriteGroup):
    pass

class FavoriteFriendGroup(FavoriteGroup):
    pass

class FavoriteAvatarGroup(FavoriteGroup):
    pass