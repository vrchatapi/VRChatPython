from ..decorators import auth_required
from .enum import FavoriteType
from ..model import Model

import logging

class Favorite(Model):
    __slots__ = ("favorite_id", "id", "tags", "type")
    __types__ = {"type": FavoriteType}

    @auth_required
    async def unfavorite(self):
        """Unfavorites this favorite"""
        logging.debug("Unfavoriting %s" % self.id)

        await self.client.request.delete("/favorites/%s" % self.id)