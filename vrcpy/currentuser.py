from __future__ import annotations

from .notification import Notification
from .decorators import auth_required
from .limiteduser import LimitedUser
from .moderation import Moderation
from .permission import Permission
from .user import User

from .types.enum import UserStatus, PlayerModerationType, ReleaseStatus
from .types.enum import NotificationType, SearchGenericType, FavoriteType
from .types.favorite import Favorite

import logging
from typing import List, Union

import vrcpy.avatar

class CurrentUser(User):
    @auth_required
    async def fetch_friends(
        self, offset: int = 0, n: int = 60, 
        offline: bool = False) -> List[LimitedUser]:
        """
        Fetches all friends

        Keyword Arguments
        ----------
        offset: :class:`int`
            Zero-based offset from start of object return\n
            Used for pagination\n
            Defaults to ``0``
        n: :class:`int`
            Number of objects to return\n 
            Min 1 | Max 100\n
            Defaults to ``60``
        offline: :class:`bool`
            Whether to return offline or online friends\n
            Defaults to ``False``
        """
        logging.debug("Fetching friend list (offset=%s n=%s offline=%s)" % (
            offset, n, offline))

        friends = await self.client.request.get("/auth/user/friends")
        friends = [LimitedUser(
            self.client, user) for user in friends[data]]

        return friends

    @auth_required
    async def create_avatar(
        self, name: str, image_url: str, asset_url: str = None, id: str = None,
        description: str = None, tags: List[str] = None,
        release_status: ReleaseStatus = None, version: int = None,
        unity_package_url: str = None) -> vrcpy.avatar.Avatar:
        """
        Creates an avatar

        Arguments
        ----------
        name: :class:`str`
            Name to give the avatar
        image_url: :class:`str`
            URL to preview image of avatar

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
        release_status: :class:`vrcpy.types.enum.ReleaseStatus`
            Release status of avatar\n
            Defaults to ``vrcpy.types.enum.ReleaseStatus.PUBLIC``
        version: :class:`int`
            Current release version of avatar\n
            Defaults to ``1``
        unity_package_url: :class:`str`
            URL to unity package for avatar\n
            Defaults to ``None``
        """
        
        names = {
            "assetUrl": asset_url,
            "id": id,
            "name": name,
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

        resp = await self.client.request.post("/avatars", json=req)
        return vrcpy.avatar.Avatar(self.client, resp["data"])

    @auth_required
    async def fetch_player_moderations(
        self, id: str = None,
        typeof: PlayerModerationType = None) -> List[Moderation]:
        """
        Fetches all player moderations user has made

        Keyword Arguments
        ------------------
        id: :class:`str`
            Only return moderations against a user with this ID\n
            Defaults to ``None``
        typeof: :class:`PlayerModerationType`
            Only return moderations of this type\n
            Defautls to ``None``
        """
        logging.debug("Fetching player moderations")

        params = {}

        if id is not None:
            params["targetUserId"] = id
        if typeof is not None:
            if typeof == PlayerModerationType.UNBLOCK:
                raise TypeError("PlayerModerationType.UNBLOCK is not allowed in this method")

            params["type"] = typeof.value

        resp = await self.client.request.get(
            "/auth/user/playermoderations",
            params=params)
        return [Moderation(self.client, mod) for mod in resp["data"]]

    @auth_required
    async def fetch_moderation(
        self, id: str) -> Moderation:
        """
        Fetches a moderation

        Arguments
        ----------
        id: :class:`str`
            ID of the moderation to fetch
        """
        logging.debug("Fetching moderation %s" % id)

        resp = await self.client.request.get("/auth/user/playermoderations/"+id)
        return Moderation(self.client, resp["data"])

    @auth_required
    async def clear_player_moderations(self):
        """Clears all moderations made by this user"""
        logging.debug("Clearing all moderations")

        await self.client.request.delete("/auth/user/playmoderations")

    @auth_required
    async def fetch_notifications(
        self, typeof: Union[
            NotificationType, SearchGenericType] = SearchGenericType.ALL,
        hidden: bool = False, after: str = None,
        n: int = 60, offset: int = 0) -> List[Notification]:
        """
        Fetches all notifications for this user

        Keyword Arguments
        ------------------
        typeof: :class:`list`[:class:`NotificationType`, :class:`SearchGenericType`]
            Fetch only notifications of this type\n
            Defaults to ``SearchGenericType.ALL
        hidden: :class:`bool`
            Include hidden notifications in result\n
            This can only be ``True`` when typeof kwarg is set to :class:`NotificationType.FRIEND_REQUEST`\n
            Defaults to ``False``
        after: :class:`str`
            Include only results after this date\n
            Defaults to ``None``
        n: :class:`int`
            Number of objects to return\n
            Defaults to ``60``
        offset: :class:`int`
            Zero-based offset from start of object return\n
            Used for pagination
            Defaults to ``0``
        """

        if hidden and typeof != NotificationType.FRIEND_REQUEST:
            raise TypeError("Hidden can be True only when typeof kwarg is set to NotificationType.FRIEND_REQUEST")

        typeof = typeof.value
        params = {}
        names = {
            "type": typeof,
            "hidden": hidden,
            "after": after,
            "n": n,
            "offset": offset
        }
        
        for param in names:
            if names[param] is not None:
                params[param] = names[param]

        resp = await self.client.request.get("/auth/user/notifications",
                                             params=params)
        return [Notification(self.client, notif) for notif in resp["data"]]

    @auth_required
    async def fetch_notification(self, id: str) -> Notification:
        """
        Fetches a notification

        Arguments
        ----------
        id: :class:`str`
            ID of the notification to fetch
        """
        logging.debug("Fetching notification %s" % id)

        resp = await self.client.request.get(
            "/auth/user/notifications/%s" % id)
        return Notification(self.client, resp["data"])

    @auth_required
    async def clear_notifications(self):
        """Clears all notifications"""
        logging.debug("Clearing all notifications")

        await self.client.request.put("/auth/user/notifications/clear")

    @auth_required
    async def fetch_permissions(self) -> List[Permission]:
        """Fetches all permissions"""
        logging.debug("Fetching permissions")

        resp = await self.client.request.get("/auth/permissions")
        return [Permission(self.client, perm) for perm in resp["data"]]

    @auth_required
    async def fetch_favorites(
        self, n: int = 60, offset: int = 0,
        typeof: FavoriteType = None, tag: List[str] = None) -> List[Favorite]:
        """
        Fetches user favorites

        Keyword Arguments
        ------------------
        n: :class:`int`
            Number of :class:`vrcpy.types.favorite.Favorite` objects to return
        offset: :class:`int`
            Zero-based offset from start of object return\n
            Used for pagination
        type: :class:`vrcpy.types.enum.FavoriteType`
            Type of favorites to return
        tags: :class:`list`[:class:`str`]
            Tags to filter by
        """
        req = {}
        names = {"n": n, "offset": offset, "tags": tags}

        for attr in names:
            if names[attr] is not None:
                req[attr] = names[attr]
        logging.debug("Listing favorites %s" % req)

        resp = await self.client.request.get("/favorites", params=req)
        return [Favorite(self.client, fav) for fav in resp["data"]]

    @auth_required
    async def update(
        self, email: str = None, birthday: str = None,
        accepted_tos_version: int = None, tags: List[str] = None,
        status: UserStatus = None, status_description: str = None,
        bio: str = None, bio_links: List[str] = None,
        user_icon: str = None) -> CurrentUser:
        """
        Updates this user

        Keyword Arguments
        ------------------
        email: :class:`str`
            Defaults to ``None``
        birthday: :class:`str`
            Defaults to ``None``
        accepted_tos_version: :class:`int`
            Defautls to ``None``
        tags: :class:`list`[:class:`str`]
            Defaults to ``None``
        status: :class:`UserStatus`
            Defaults to ``None``
        status_description: :class:`str`
            Defaults to ``None``
        bio: :class:`str`
            Defaults to ``None``
        bio_links: :class:`list`[:class:`str`]
            Defaults to ``None``
        user_icon: :class:`str`
            Defaults to ``None``
        """

        names = {
            "email": email,
            "birthday": birthday,
            "acceptedTOSVersion": accepted_tos_version,
            "tags": tags,
            "status": None if status is None else status.value,
            "statusDescription": status_description,
            "bio": bio,
            "bioLinks": bio_links,
            "userIcon": user_icon
        }

        req = {}

        for attr in names:
            if names[attr] is not None:
                req[attr] = names[attr]

        resp = await self.client.request.put("/users/%s" % self.id, json=req)
        return CurrentUser(self.client, resp["data"])

    @auth_required
    async def delete_account(self) -> CurrentUser:
        """Queues users account for deletion"""
        logging.debug("Deleting user %s" % self.id)

        resp = await self.client.request.put("/user/%s/delete" % self.id)
        self.client.me = CurrentUser(self.client, resp["data"])

        return self.client.me