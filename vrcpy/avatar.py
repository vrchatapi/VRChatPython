from vrcpy.baseobject import BaseObject
from vrcpy.enum import FavoriteType
from vrcpy.errors import ObjectErrors

import logging


class Avatar(BaseObject):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop=loop)

        self.required.update({
            "name": {
                "dict_key": "name",
                "type": str
            },
            "description": {
                "dict_key": "description",
                "type": str
            },
            "id": {
                "dict_key": "id",
                "type": str
            },
            "author_name": {
                "dict_key": "authorName",
                "type": str
            },
            "author_id": {
                "dict_key": "authorId",
                "type": str
            },
            "tags": {
                "dict_key": "tags",
                "type": str
            },
            "version": {
                "dict_key": "version",
                "type": str
            },
            "featured": {
                "dict_key": "featured",
                "type": str
            },
            "created_at": {
                "dict_key": "created_at",
                "type": str
            },
            "updated_at": {
                "dict_key": "updated_at",
                "type": str
            },
            "release_status": {
                "dict_key": "releaseStatus",
                "type": str
            },
            "platform": {
                "dict_key": "platform",
                "type": str
            },
            "image_url": {
                "dict_key": "imageUrl",
                "type": str
            },
            "thumbnail_image_url": {
                "dict_key": "thumbnailImageUrl",
                "type": str
            },
            "unity_version": {
                "dict_key": "unityVersion",
                "type": str
            }
        })

        self.optional.update({
            "asset_url": {
                "dict_key": "assetUrl",
                "type": str
            }
        })

        self._assign(obj)

    async def favorite(self):
        '''
        Favorite this avatar
        Returns an AvatarFavorite object
        '''

        logging.debug("Favoriting avatar with id " + self.id)

        resp = await self.client.request.call(
            "/favorites",
            "POST",
            params={
                "type": "avatar",
                "favoriteId": self.id,
                "tags": ["avatars1"]
            }
        )

        this = self.client._BaseFavorite.build_favorite(
            self.client, resp["data"], self.loop)
        self.client.favorites[FavoriteType.Avatar].append(this)

        return this

    async def delete(self):
        '''
        Deletes this avatar
        '''

        if self.client.me.id != self.author_id:
            raise ObjectErrors.NotOwned("Can't modify not-owned avatar")

        logging.debug("Deleted avatar " + self.id)
        await self.client.request("/avatars/"+self.id, "DELETE")

        del self

    async def choose(self):
        '''
        Sets this avatar to use
        '''

        logging.debug("Setting current avatar to " + self.id)

        await self.client.request.call(
            "/avatars/%s/select" % self.id, "PUT")
