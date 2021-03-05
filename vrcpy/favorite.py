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

        await self.client.request.call("/favorites/"+self.id, "DELETE")
        logging.debug("Unfavorited %s %s" % (self.type, self.id))


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
