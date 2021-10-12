from ..decorators import auth_required
from .enum import FavoriteType
from ..model import Model
from .rdict import RDict

import logging

class Favorite(Model):
    __slots__ = ("favorite_id", "id", "tags", "type")
    __types__ = RDict({"type": FavoriteType})

    async def unfavorite(self):
        """Unfavorites this favorite"""
        await self.client.delete_favorite(self.id)