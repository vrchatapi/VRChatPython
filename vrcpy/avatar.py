from __future__ import annotations

from .types.enum import ReleaseStatus
from .decorators import auth_required
from .model import Model
from typing import List

import vrcpy.currentuser

class Avatar(Model):
    __slots__ = (
        "asset_url", "asset_url_object", "author_id", "author_name",
        "created_at", "description", "featured", "id", "image_url", "name",
        "release_status", "tags", "thumbnail_image_url", "unity_package_url",
        "unity_packages", "updated_at", "version"
    )

    async def select(self) -> vrcpy.currentuser.CurrentUser:
        """Selects this avatar"""
        resp = await self.client.select_avatar(self.id)
        return resp

    @auth_required
    async def update(
        self, asset_url: str = None, id: str = None, description: str = None,
        tags: List[str] = None, image_url: str = None,
        release_status: ReleaseStatus = None, version: int = None,
        unity_package_url: str = None) -> Avatar:
        """
        Updates this avatar

        Keyword Arguments
        ------------------
        asset_url: :class:`str`
            URL to avatar asset (.vrca)\n
            Defaults to ``None``
        id: :class:`str`
            Custom ID to give avatar\n
            Defaults to ``None``
        description: :class:`str`
            Description of avatar\n
            Defaults to ``None``
        tags: :class:`list`[:class:`str`]
            Avatar tags\n
            Defaults to ``None``
        image_url: :class:`str`
            URL to preview image of avatar\n
            Defaults to ``None``
        release_status: :class:`vrcpy.types.enum.ReleaseStatus`
            Release status of avatar\n
            Defaults to ``None``
        version: :class:`int`
            Current release version of avatar\n
            Defaults to ``None``
        unity_package_url: :class:`str`
            URL to unity package for avatar\n
            Defaults to ``None``
        """

        names = {
            "assetUrl": asset_url,
            "id": id,
            "description": description,
            "tags": tags,
            "imageUrl": image_url,
            "releaseStatus": None if release_status is None else release_status.value,
            "version": version,
            "unityPackageUrl": unity_package_url
        }

        req = {}
        for item in names:
            if names[item] is not None:
                req[item] = names[item]

        resp = await self.client.request.put("/avatars", json=req)
        return Avatar(self.client, resp["data"])

    async def delete(self) -> Avatar:
        """Deletes this avatar"""
        resp = await self.client.delete_avatar(self.id)
        return resp