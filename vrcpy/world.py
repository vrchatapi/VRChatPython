from __future__ import annotations

from .limitedworld import LimitedWorld
from .decorators import auth_required

import logging

class World(LimitedWorld):
    __slots__ = (
        "asset_url", "asset_url_obj", "description", "featured"
        "instance", "labs_publication_date", "name", "namespace",
        "plugin_url_object", "preview_youtube_id", "private_occupants",
        "public_occupants", "unity_package_url_object",
        "version", "visits"
    )

    @auth_required
    async def update(
        self, asset_url: str = None, author_id: str = None,
        author_name: str = None, capacity: int = None, id: str = None,
        description: str = None, tags: List[str] = None,
        image_url: str = None, name: str = None, platform: str = None,
        release_status: ReleaseStatus = None, version: int = None,
        unity_package_url: str = None, unity_version: str = None) -> Avatar:
        """
        Updates this avatar

        Keyword Arguments
        ------------------
        asset_url: :class:`str`
            URL to world asset (.vrcw)
        author_id: :class:`str`
            ID of the user who owns the world
        author_name: :class:`str`
            Name of the user who owns the world
        capacity: :class:`str`
            Instance capacity of this world
        id: :class:`str`
            Custom ID to give world
        description: :class:`str`
            Description of world
        tags: :class:`list`[:class:`str`]
            World tags
        image_url: :class:`str`
            URL to preview image of world
        name: :class:`str`
            Name of the world
        platform: :class:`str`
            Platform the world supports
        release_status: :class:`vrcpy.types.enum.ReleaseStatus`
            Release status of world
        version: :class:`int`
            Current release version of world
        unity_package_url: :class:`str`
            URL to unity package for world
        unity_version: :class:`str`
            Version of unity this world was uploaded from
        """
        req = {}
        names = {
            "assetUrl": asset_url,
            "authorId": author_id,
            "authorName": author_name,
            "capacity": capacity,
            "id": id,
            "description": description,
            "tags": tags,
            "imageUrl": image_url,
            "name": name,
            "platform": platform,
            "releaseStatus": None if release_status is None else release_status.value,
            "assetVersion": version,
            "unityPackageUrl": unity_package_url,
            "unityVersion": unity_version
        }
        
        for item in names:
            if names[item] is not None:
                req[item] = names[item]

        logging.debug("Updating world %s" % req)

        resp = await self.client.request.put("/worlds", json=req)
        return World(self.client, resp["data"])

    @auth_required
    async def delete(self):
        """Deletes this world"""
        logging.debug("Deleting world %s" % self.id)

        await self.client.request.delete("/worlds/%s" % self.id)