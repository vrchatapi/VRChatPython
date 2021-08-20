from vrcpy.enum import FavoriteType
from vrcpy.errors import ObjectErrors
from vrcpy.baseobject import BaseObject
from vrcpy.favorite import BaseFavorite

import logging


class Avatar(BaseObject):
    """
    Represents a VRChat avatar.\n
    You should not instantiate this class manually

    Attributes
    ----------
    name: :class:`str`
        Name of the avatar
    description: :class:`str`
        Description of the avatar
    id: :class:`str`
        Unique avatar ID
    author_name: :class:`str`
        Username of user who uploaded avatar
    author_id: :class:`str`
        Unique user ID of the user who uploaded avatar
    version: :class:`int`
        Version of the avatar
    favorite_group_name: :class:`str`
        Favorite group name, ``None`` if not favorited
    favorite_id: :class:`str`
        Favorite ID, ``None`` if not favorited
    created_at: :class:`str`
        Timedate when avatar was created
    tags: :class:`list`
        List of :class:`str` tags
    updated_at: :class:`str`
        Timedate when avatar was last updated
    featured: :class:`bool`
        If avatar is featured
    image_url: :class:`str`
        URL for image of avatar
    thumbnail_image_url: :class:`str`
        URL for thumbnail image of avatar
    release_status: :class:`str`
        Release status of avatar
    """

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
                "type": list
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
            "image_url": {
                "dict_key": "imageUrl",
                "type": str
            },
            "thumbnail_image_url": {
                "dict_key": "thumbnailImageUrl",
                "type": str
            }
        })

        self.optional.update({
            "favorite_group_name": {
                "dict_key": "favoriteGroup",
                "type": str
            },
            "favorite_id": {
                "dict_key": "favoriteId",
                "type": str
            }
        })

        self._assign(obj)

    async def favorite(self):
        """
        Favorites this avatar, returns a :class:`vrcpy.AvatarFavorite` object
        """

        logging.debug("Favoriting avatar with id " + self.id)

        resp = await self.client.request.post(
            "/favorites",
            params={
                "type": "avatar",
                "favoriteId": self.id,
                "tags": ["avatars1"]
            }
        )

        this = BaseFavorite.build_favorite(
            self.client, resp["data"], self.loop)
        self.client.favorites[FavoriteType.AVATAR].append(this)

        return this

    async def delete(self):
        """Deletes this avatar"""

        if self.client.me.id != self.author_id:
            raise ObjectErrors.NotOwned("Can't modify not-owned avatar")

        logging.debug("Deleted avatar " + self.id)
        await self.client.request("/avatars/"+self.id, "DELETE")

        del self

    async def choose(self):
        """Sets this avatar to use"""

        logging.debug("Setting current avatar to " + self.id)

        await self.client.request.put(
            "/avatars/%s/select" % self.id)
