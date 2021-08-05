from vrcpy.baseobject import BaseObject

import logging

class BaseFavorite(BaseObject):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop)

        self.required.update({
            "id": {
                "dict_key": "id",
                "type": str
            },
            "type": {
                "dict_key": "type",
                "type": str
            }
        })

        self.favorite_group = obj["tags"][0]

    @staticmethod
    def build_favorite(client, obj, loop=None):
        switch = {
            "world": WorldFavorite,
            "friend": FriendFavorite,
            "avatar": AvatarFavorite
        }

        logging.debug("Building favorite of type " + obj["type"])

        return switch[obj["type"]](client, obj, loop)

    async def unfavorite(self):
        '''
        Unfavorites this favorite object
        '''

        await self.client.request.delete("/favorites/"+self.id)
        logging.debug("Unfavorited %s %s" % (self.type, self.id))

class FavoriteGroup(BaseFavorite):
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

class WorldFavorite(BaseFavorite):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, obj, loop)

        self.required.update({
            "world_id": {
                "dict_key": "favoriteId",
                "type": str
            }
        })

        self._assign(obj)


class AvatarFavorite(BaseFavorite):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, obj, loop)

        self.required.update({
            "avatar_id": {
                "dict_key": "favoriteId",
                "type": str
            }
        })

        self._assign(obj)


class FriendFavorite(BaseFavorite):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, obj, loop)

        self.required.update({
            "user_id": {
                "dict_key": "favoriteId",
                "type": str
            }
        })

        self._assign(obj)
