from vrcpy.baseobject import BaseObject
from vrcpy.enum import FavoriteType

import logging

class BaseFavorite(BaseObject):
    """Base favorite class that all favorites objects are built on top of"""

    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop)

        self.required.update({
            "id": {
                "dict_key": "id",
                "type": str
            },
            "type": {
                "dict_key": "type",
                "type": FavoriteType
            }
        })

        self.favorite_group = obj["tags"][0]

    @staticmethod
    def build_favorite(client, obj, loop=None):
        switch = {
            FavoriteType.WORLD: WorldFavorite,
            FavoriteType.FRIEND: FriendFavorite,
            FavoriteType.AVATAR: AvatarFavorite
        }

        logging.debug("Building favorite of type " + obj["type"])

        return switch[FavoriteType[obj["type"].upper()]](client, obj, loop)

    async def unfavorite(self):
        """Unfavorites the favorite object"""

        await self.client.request.delete("/favorites/"+self.id)
        logging.debug("Unfavorited %s %s" % (self.type, self.id))

class FavoriteGroup(BaseFavorite):
    """Base favorite class that all favorite group objects are built on top of"""

    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop)

        self.required.update({
            "display_name": {
                "dict_key": "displayName",
                "type": str
            },
            "name": {
                "dict_key": "name",
                "type": str
            },
            "owner_display_name": {
                "dict_key": "ownerDisplayName",
                "type": str
            },
            "owner_id": {
                "dict_key": "ownerId",
                "type": str
            },
            "tags": {
                "dict_key": "tags",
                "type": list
            },
            "visibility": {
                "dict_key": "visibility",
                "type": str
            }
        })

        del self.unfavorite
        self._assign(obj)
        self.favorites = []

    @staticmethod
    def build_favorite_group(client, obj, loop=None):
        switch = {
            FavoriteType.WORLD: WorldFavoriteGroup,
            FavoriteType.FRIEND: FriendFavoriteGroup,
            FavoriteType.AVATAR: AvatarFavoriteGroup
        }

        logging.debug("Building favorite group of type " + obj["type"])

        return switch[FavoriteType(obj["type"])](client, obj, loop)

class WorldFavorite(BaseFavorite):
    """Represents a favorite world"""

    def __init__(self, client, obj, loop=None):
        super().__init__(client, obj, loop)

        self.required.update({
            "world_id": {
                "dict_key": "favoriteId",
                "type": str
            }
        })

        self._assign(obj)

class WorldFavoriteGroup(FavoriteGroup):
    """Represents a favorite world group"""
    pass

class AvatarFavorite(BaseFavorite):
    """Represents a favorite avatar"""

    def __init__(self, client, obj, loop=None):
        super().__init__(client, obj, loop)

        self.required.update({
            "avatar_id": {
                "dict_key": "favoriteId",
                "type": str
            }
        })

        self._assign(obj)

class AvatarFavoriteGroup(FavoriteGroup):
    """Represents a favorite avatar group"""
    pass

class FriendFavorite(BaseFavorite):
    """Represents a favorite (or grouped) friend"""

    def __init__(self, client, obj, loop=None):
        super().__init__(client, obj, loop)

        self.required.update({
            "user_id": {
                "dict_key": "favoriteId",
                "type": str
            }
        })

        self._assign(obj)

class FriendFavoriteGroup(FavoriteGroup):
    """Represents a favorite friend group"""
    pass