from .errors import ClientErrors
from .http import Request

from .favoritegroup import FavoriteGroup
from .util.threadwrap import ThreadWrap
from .notification import Notification
from .decorators import auth_required
from .currentuser import CurrentUser
from .limiteduser import LimitedUser
from .permission import Permission
from .avatar import Avatar
from .config import Config
from .world import World
from .user import User

from .types.enum import DeveloperType, Sort, UserFilter
from .types.enum import SortOrder, ReleaseStatus, FavoriteType
from .types.instance import Instance
from .types.favorite import Favorite

import vrcpy.currentuser

import logging
import asyncio
import base64
import time
import json

from typing import Union, List, Dict, Callable

class Client:
    """
    VRChat Client object used to interact with the VRChat API

    Keyword Arguments
    ------------------
    loop: :class:`asyncio.AbstractEventLoop`
        Event loop client will create new asyncio tasks in.
        Defaults to ``None``

    Attributes
    -----------
    config: :class:`vrcpy.config.Config`
        Last fetched API Configuration
    loop: :class:`asyncio.AbstractEventLoop`
        Event loop client will create new asyncio tasks in.
    me: :class:`vrcpy.currentuser.CurrentUser`
        Last fetched user profile object
    request: :class:`vrcpy.http.Request`
        Internal AIOHTTP Wrapper instance
    users: :class:`list`
        User cache
    ws: :class:`aiohttp.ClientWebSocketResponse`
        Websocket connection to VRChat
    """

    def __init__(self, loop=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.me = None
        self.config = None
        self.request = Request(self)
        self.ws = None

        self._logged_in = False
        self._logout_intent = False
        self._event_listeners = []

        ## Cache
        self.users = []

    async def _pre_loop(self):
        # Fetch all friends
        # I want this to be able to be run no matter cache state,
        # and be successful

        count = 0
        for offset in range(0, len(self.me.friends), 100):
            friends = await self.me.fetch_friends(offset, 100, False)
            self.users += friends

            my_count = len(friends)
            count += my_count

            if my_count > 100:
                break

        for offset in range(0, len(self.me.friends) - count, 100):
            friends = await self.me.fetch_friends(offset, 100, True)
            self.users += friends

        self.loop.create_task(self.on_ready())

    def run(self, username: str, password: str, mfa: str = None):
        """
        Automates :func:`Client.login` + :func:`Client.start_ws_loop`
        This function is blocking

        Arguments
        ----------
        username: :class:`str`
            Username/email of VRChat account
        password: :class:`str`
            Password of VRChat account


        Keyword Arguments
        ------------------
        mfa: :class:`str`
            One Time Password (OTP, recovery code) or Timed One Time Password (TOTP, MFA code) to verify auth cookie
        """

        async def run():
            await self.login(username, password, mfa)
            await self.start_ws_loop()

        try:
            self.loop.run_until_complete(run())
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.logout())
        except Exception as e:
            self.loop.run_until_complete(self.logout())
            raise e.__class__(str(e))

    # Cache grabbers

    def get_user(self, id: str) -> Union[User, LimitedUser, None]:
        """
        Get a user from cache
        Returns None if user not in cache

        Arguments
        ----------
        id: :class:`str`
            ID of the user to get
        """
        for user in self.users:
            if user.id == id:
                return user

        return None

    def get_friends(self) -> List[Union[User, LimitedUser]]:
        """Gets all cached friends"""
        return [user for user in self.users if user.is_friend]

    def get_active_friends(self) -> List[Union[User, LimitedUser]]:
        """Gets all cached friends that are active"""
        return [
            user for user in self.get_friends() if user.status == "active"]

    def get_online_friends(self) -> List[Union[User, LimitedUser]]:
        """Gets all cached friends that are online"""
        return [
            user for user in self.get_friends() if user.status == "online"]

    def get_offline_friends(self) -> List[Union[User, LimitedUser]]:
        """Gets all cached friends that are offline"""
        return [
            user for user in self.get_friends() if user.status == "offline"]

    # Fetches

    @auth_required
    async def fetch_me(self) -> vrcpy.currentuser.CurrentUser:
        """
        Fetches new CurrentUser object.
        This also updates `Client.me`
        """

        logging.debug("Fetching CurrentUser")

        me = await self.request.get("/auth/user")
        me = vrcpy.currentuser.CurrentUser(self, me["data"])

        self.me = me
        return me

    @auth_required
    async def search_users(
        self, search: str, developer_type: DeveloperType = None, n: int = 60,
        offset: int = 0) -> List[User]:
        """
        Searches VRChat for users

        Arguments
        ----------
        search: :class:`str`
            User display name to search for

        Keyword Arguments
        ------------------
        developer_type: :class:`vrcpy.types.enum.DeveloperType`
            Only return users that have this developer type
            Defaults to ``vrcpy.types.enum.DeveloperType.NONE``
        n: :class:`int`
            Number of objects to return
            Min 1 | Max 100
            Defaults to ``60``
        offset: :class:`int`
            Zero-based offset from start of object return
            Used for pagination
            Defaults to ``0``
        """
        logging.debug(
            "Searching users (search={} devType={} n={} offset={})".format(
                search, developer_type, n, offset))

        names = {
            "search": search,
            "developerType": None if developer_type is None else developer_type.value,
            "n": n,
            "offset": offset
        }

        req = {}

        for param in names:
            if names[param] is not None:
                req[param] = names[param]

        users = await self.request.get("/users", params=req)
        return [User(self, user) for user in users["data"]]

    @auth_required
    async def fetch_user(self, id: str) -> User:
        """
        Fetches a user using their id

        Arguments
        ----------
        id: :class:`str`
            ID of the user to fetch
        """
        logging.debug("Fetching user %s" % id)

        resp = await self.request.get("/users/"+id)
        return User(self, resp["data"])

    @auth_required
    async def fetch_user_via_username(self, username: str) -> User:
        """
        Fetches a user using their username

        Arguments
        ----------
        username: :class:`str`
            Username of the user to fetch
        """
        logging.debug("Fetching user via username %s" % id)

        resp = await self.request.get("/users/%s/name" % username)
        return User(self, resp["data"])

     @auth_required
    async def friend_user(self, id: str) -> Notification:
        """
        Sends a :class:`PlayerModerationType.FRIEND_REQUEST` notification to a user

        Arguments
        ----------
        id: :class:`str`
            ID of the user to friend
        """
        logging.debug("Friending %s" % id)

        resp = await self.request.post("/auth/%s/friendRequest" % id)
        return Notification(self, resp["data"])

    @auth_required
    async def cancel_friend(self, id: str):
        """
        Cancels a :class:`PlayerModerationType.FRIEND_REQUEST` notification that was sent to a user
        
         Arguments
        ----------
        id: :class:`str`
            ID of the user to cancel friend request to
        """
        logging.debug("Cancelling friend request to %s" % id)
        await self.request.delete("/user/%s/friendRequest" % id)

    @auth_required
    async def fetch_friend_status(self) -> Dict[str, bool]:
        """
        Gets the friend status of this user
        
        Arguments
        ----------
        id: :class:`str`
            ID of the user to fetch friend status with
        """
        logging.debug("Fetching friend status for %s" % id)

        resp = await self.request.get("/user/%s/friendStatus" % id)
        resp = {
            "incoming_request": resp["data"]["incomingRequest"],
            "is_friend": resp["data"]["isFriend"],
            "outgoing_request": resp["data"]["outgoingRequest"]
        }

        return resp

    @auth_required
    async def unfriend_user(self, id: str):
        """
        Unfriends a user

        Arguments
        ----------
        id: :class:`str`
            ID of the user to unfriend
        """
        logging.debug("Unfriending %s" % id)
        await self.request.delete("/auth/user/friends/%s" % id)

    @auth_required
    async def fetch_avatar(self, id: str) -> Avatar:
        """
        Fetches an avatar object

        Arguments
        ----------
        id: :class:`str`
            ID of avatar to fetch
        """
        logging.debug("Fetching avatar %s" % id)

        resp = await self.request.get("/avatar/%s" % id)
        return Avatar(self, resp["data"])

    @auth_required
    async def search_avatars(
        self, sort: Sort = Sort.POPULARITY, user: UserFilter = UserFilter.NONE,
        user_id: str = None, n: int = 60, featured: bool = True,
        order: SortOrder = SortOrder.DESCENDING, offset: int = 0,
        tag: List[str] = None, notag: List[str] = None,
        release_status: ReleaseStatus = ReleaseStatus.PUBLIC,
        max_unity_version: str = None, min_unity_version: str = None,
        platform: str = None) -> List[Avatar]:
        """
        Search for avatars with filters
        You can only search your own or featured avatars

        Keyword Arguments
        ------------------
        sort: :class:`vrcpy.types.enum.Sort`
            What to sort result by\n
            Defaults to ``vrcpy.types.enum.Sort.POPULARITY``
        user: :class:`vrcpy.types.enum.UserFilter`
            User to filter avatars by\n
            Defaults to ``vrcpy.types.enum.UserFilter.NONE``
        user_id: :class:`str`
            ID of user to filter avatars by\n
            Defaults to ``None``
        n: :class:`int`
            Number of objects to return\n
            Min 1 | Max 100\n
            Defaults to ``60``
        featured: :class:`bool`
            Filters to only featured results\n
            Defaults to ``True``
        order: :class:`vrcpy.types.enum.SortOrder`
            Order to list sorted items in\n
            Defaults to ``vrcpy.types.enum.SortOrder.DESCENDING``
        offset: :class:`int`
            Zero-based offset from start of object return\n
            Used for pagination\n
            Defaults to ``0``
        tag: :class:`list`[:class:`str`]
            Tags to include\n
            Defaults to ``None``
        notag: :class:`list`[:class:`str`]
            Tags to exclude\n
            Defaults to ``None``
        release_status: :class:`vrcpy.types.enum.ReleaseStatus`
            Filter by release status\n
            Defaults to ``vrcpy.types.enum.ReleaseStatus.PUBLIC``
        max_unity_version: :class:`str`
            Maximum unity version supported by the .vrca asset\n
            Defaults to ``None``
        min_unity_version: :class:`str`
            Minimum unity version supported by the .vrca asset\n
            Defaults to ``None``
        platform: :class:`str`
            Platform the .vrca asset supports\n
            Defaults to ``None``
        """

        names = {
            "sort": None if sort is None else sort.value,
            "user": None if user is None else user.value,
            "userId": user_id,
            "n": n,
            "order": None if order is None else order.value,
            "offset": offset,
            "tag": tag,
            "notag": notag,
            "releaseStatus": None if release_status is None else release_status.value,
            "maxUnityVersion": max_unity_version,
            "minUnityVersion": min_unity_version,
            "platform": platform
        }

        req = {}
        for attr in names:
            if attr is not None:
                req[attr] = names[attr]

        logging.debug("Searching avatar %s" % req)

        resp = await self.request.get("/avatars", json=req)
        return [Avatar(self, avatar) for avatar in resp["data"]]

    @auth_required
    async def select_avatar(self, id: str) -> CurrentUser:
        """
        Selects avatar
        
        Arguments
        ----------
        id: :class:`str`
            ID of avatar to select
        """
        logging.debug("Selecting avatar %s" % id)

        resp = await self.request.put("/avatars/%s/select" % id)
        self.me = CurrentUser(self, resp["data"])
        return self.me

    @auth_required
    async def delete_avatar(self, id: str) -> Avatar:
        """
        Deletes avatar
        
        Arguments
        ----------
        id: :class:`str`
            ID of avatar to delete
        """
        logging.debug("Deleting avatar %s" % id)

        resp = await self.request.delete("/avatars/%s" % id)
        return Avatar(self, resp["data"])

    @auth_required
    async def fetch_permission(self, id: str) -> Permission:
        """
        Fetches a permission

        Arguments
        ----------
        id: :class:`str`
            ID of permission to fetch
        """
        logging.debug("Fetching permission %s" % id)

        resp = await self.request.get("/permissions/%s" % id)
        return Permission(self, resp["data"])

    @auth_required
    async def fetch_favorite_group(
        self, favorite_group_type: FavoriteType, 
        name: str, user_id: str) -> FavoriteGroup:
        """
        Fetches a favorite group

        Arguments
        ----------
        favorite_group_type: :class:`vrcpy.types.enum.FavoriteType`
            Type of group to fetch
        name: :class:`str`
            Name of group to fetch
        user_id: :class:`str`
            User who owns the :class:`vrcpy.favoritegroup.FavoriteGroup`
        """
        logging.debug(
            "Fetching FavoriteGroup \{{}: {}, {}: {}, {}: {}\}".format(
                "favorite_group_type", favorite_group_type,
                "name", name, "user_id", user_id))
        
        resp = await self.request.get("/favorite/group/%s/%s/%s" % (
            favorite_group_type.value, name, user_id))
        return FavoriteGroup.favorite_group(self, resp["data"])

    @auth_required
    async def fetch_favorite(self, id: str) -> Favorite:
        """
        Fetches a favorite

        Arguments
        ----------
        id: :class:`str`
            ID of the favorite object
        """
        logging.debug("Fetching favorite %s" % id)

        resp = await self.request.get("/favorites/%s" % id)
        return Favorite(self, resp["data"])

    @auth_required
    async def add_favorite(
        self, typeof: FavoriteType, id: str, group_name: str) -> Favorite:
        """
        Favorites an object

        Arguments
        ----------
        typeof: :class:`vrcpy.types.enum.FavoriteType`
            Type of object to favorite
        id: :class:`str`
            ID of friend, avatar or world to favorite
        group_name: :class:`str`
            Name of group to add favorite to
        """
        logging.debug("Adding %s object (%s) to %s favorite group" % (
            typeof, id, group_name))

        resp = await self.request.post("/favorites", json={
            "type": typeof.value, "favoriteId": id, "tags": [group_name]})
        return Favorite(self, resp["data"])

    @auth_required
    async def delete_favorite(self, id: str):
        """
        Deletes a favorite

        Arguments
        ----------
        id: :class:`str`
            ID of the favorite object
        """
        logging.debug("Unfavoriting %s" % id)
        await self.client.request.delete("/favorites/%s" % id)

    @auth_required
    async def fetch_world(self, id: str) -> World:
        """
        Fetches a world

        Arguments
        ----------
        id: :class:`str`
            ID of the world object
        """
        logging.debug("Fetching world %s" % id)

        resp = await self.request.get("/worlds/%s" % id)
        return World(self, resp["data"])

    @auth_required
    async def search_worlds(
        self, search: str = None, active: bool = False, recent: bool = False,
        sort: Sort = Sort.POPULARITY, user: UserFilter = UserFilter.NONE,
        user_id: str = None, n: int = 60, featured: bool = True,
        order: SortOrder = SortOrder.DESCENDING, offset: int = 0,
        tag: List[str] = None, notag: List[str] = None,
        release_status: ReleaseStatus = ReleaseStatus.PUBLIC,
        max_unity_version: str = None, min_unity_version: str = None,
        platform: str = None) -> List[World]:
        """
        Search for worlds with filters

        Keyword Arguments
        ------------------
        search: :class:`str`
            Search for worlds by name
        active: :class:`bool`
            Search for only active worlds\n
            If True `recent` kwarg must be False
        recent: :class:`bool`
            Search for only recent worlds\n
            If True `active` kwarg must be False
        sort: :class:`vrcpy.types.enum.Sort`
            What to sort result by
        user: :class:`vrcpy.types.enum.UserFilter`
            User to filter worlds by
        user_id: :class:`str`
            ID of user to filter worlds by
        n: :class:`int`
            Number of objects to return\n
            Min 1 | Max 100
        featured: :class:`bool`
            Filters to only featured results
        order: :class:`vrcpy.types.enum.SortOrder`
            Order to list sorted items in
        offset: :class:`int`
            Zero-based offset from start of object return\n
            Used for pagination
        tag: :class:`list`[:class:`str`]
            Tags to include
        notag: :class:`list`[:class:`str`]
            Tags to exclude
        release_status: :class:`vrcpy.types.enum.ReleaseStatus`
            Filter by release status
        max_unity_version: :class:`str`
            Maximum unity version supported by the .vrcw asset
        min_unity_version: :class:`str`
            Minimum unity version supported by the .vrcw asset
        platform: :class:`str`
            Platform the .vrcw asset supports
        """

        end = ""
        if active and recent:
            raise TypeError(
                "Both active and recent kwargs can not be set to true")
        elif active:
            end = "/active"
        elif recent:
            end = "/recent"

        req = {}
        names = {
            "search": search,
            "sort": None if sort is None else sort.value,
            "user": None if user is None else user.value,
            "userId": user_id,
            "n": n,
            "order": None if order is None else order.value,
            "offset": offset,
            "tag": tag,
            "notag": notag,
            "releaseStatus": None if release_status is None else release_status.value,
            "maxUnityVersion": max_unity_version,
            "minUnityVersion": min_unity_version,
            "platform": platform
        }

        for attr in names:
            if attr is not None:
                req[attr] = names[attr]

        logging.debug("Searching world %s" % req)

        resp = await self.request.get("/worlds%s" % end, json=req)
        return [World(self, world) for world in resp["data"]]

    @auth_required
    async def create_world(
        self, asset_url: str, image_url: str, name: str,
        author_id: str = None, author_name: str = None, capacity: int = None,
        id: str = None, description: str = None, tags: List[str] = None,
        platform: str = None, release_status: ReleaseStatus = None,
        version: int = None, unity_package_url: str = None,
        unity_version: str = None) -> Avatar:
        """
        Creates a world

        Arguments
        ----------
        asset_url: :class:`str`
            URL to world asset (.vrcw)
        image_url: :class:`str`
            URL to preview image of world
        name: :class:`str`
            Name of the world

        Keyword Arguments
        ------------------
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

        logging.debug("Creating world %s" % req)

        resp = await self.request.post("/worlds", json=req)
        return World(self, resp["data"])

    @auth_required
    async def fetch_world_instance(
        self, world_id: str, instance_id: str) -> Instance:
        """
        Fetches an instance of a world

        Arguments
        ----------
        world_id: :class:`str`
            ID of the world the instance belongs to
        instance_id: :class:`str`
            ID of the instance to fetch, including nonce and region if applicable
        """
        logging.debug("Fetching instance %s/%s" % (world_id, instance_id))

        resp = await self.request.get("/worlds/%s/%s" % (
            world_id, instance_id))
        return Instance(self, resp["data"])

    @auth_required
    async def can_publish_world(self, id: str) -> bool:
        """
        Returns whether a world can be published or not
        
        Arguments
        ----------
        id: :class:`str`
            ID of world to check
        """
        logging.debug("Fetching world publish status %s" % id)

        resp = await self.request.get("/worlds/%s/publish" % id)
        return resp["data"]["canPublish"]

    @auth_required
    async def publish_world(self, id: str):
        """
        Publishes a world
        
        Arguments
        ----------
        id: :class:`str`
            ID of the world to publish
        """
        logging.debug("Publishing world %s" % id)
        await self.request.put("/worlds/%s/publish" % id)

    @auth_required
    async def unpublish_world(self, id: str):
        """
        Unpublishes a world
        
        Arguments
        ----------
        id: :class:`str`
            ID of the world to unpublish
        """
        logging.debug("Unpublishing world %s" % id)
        await self.request.delete("/worlds/%s/publish" % id)

    @auth_required
    async def delete_world(self, id: str):
        """
        Deletes a world
        
        Arguments
        ----------
        id: :class:`str`
            ID of the world to delete
        """
        logging.debug("Deleting world %s" % id)
        await self.request.delete("/worlds/%s" % id)

    @auth_required
    async def delete_moderation(self, id: str):
        """
        Deletes a moderation
        
        Arguments
        ----------
        id: :class:`str`
            ID of the moderation to delete
        """
        logging.debug("Deleting moderation %s" % id)
        await self.request.delete("/auth/user/playermoderations/%s" % id)

    @auth_required
    async def mark_notification_as_read(self, id: str) -> Notification:
        """
        Marks a notification as read
        
        Arguments
        ----------
        id: :class:`str`
            ID of the notification to mark seen
        """
        logging.debug("Marking notification as read %s" % id)

        resp = await self.request.put(
            "/auth/user/notifications/%s/see" % id)
        return Notification(self, resp["data"])

    @auth_required
    async def delete_notification(self, id: str) -> Notification:
        """
        Deletes a notification
        
        Arguments
        ----------
        id: :class:`str`
            ID of the notification to delete
        """
        logging.debug("Deleting notification %s" % id)

        resp = await self.request.put("/auth/user/notifications/%s/hide" % id)
        return Notification(self.client, resp["data"])

    ## System

    async def fetch_config(self) -> Config:
        """Fetches API Configuration"""

        logging.debug("Fetching API config")

        async with self.request.session.get(
            self.request.base + "/config") as resp:

            assert resp.status == 200
            json = await resp.json()
            self.config = Config(self, json)
        return self.config

    async def fetch_system_time(self) -> time.struct_time:
        """Fetches current VRChat system time"""
        logging.debug("Fetching system time")

        data = await self.request.get("/time")
        return time.strptime(data["data"], "%Y-%m-%dT%H:%M:%S%z")

    async def fetch_online_user_count(self) -> int:
        """Fetches current users online in VRChat"""
        logging.debug("Fetching online user count")

        data = await self.request.get("/visits")
        return data["data"]

    async def fetch_frontend_css(self) -> str:
        logging.debug("Fetching frontend CSS")

        async with self.request.session.get(
            self.request.base + "/css/app.js") as resp:
            
            assert resp.status == 200
            js = await resp.read()
        return js

    async def fetch_frontend_js(self) -> str:
        logging.debug("Fetching frontend JS")

        async with self.request.session.get(
            self.request.base + "/js/app.js") as resp:
            
            assert resp.status == 200
            js = await resp.read()
        return js

    ## Authentication

    async def login(self, username, password, mfa=None):
        """
        Logs in to vrchat
        Arguments
        ----------
        username: :class:`str`
            Username/email of VRChat account
        password: :class:`str`
            Password of VRChat account
        Keyword Arguments
        ------------------
        mfa: :class:`str`
            One Time Password (OTP, recovery code) or Timed One Time Password (TOTP, MFA code) to verify auth cookie
        """

        b64 = base64.b64encode((username+":"+password).encode()).decode()

        try:
            resp = await self.request.get("/auth/user", headers={
                "Authorization": "Basic "+b64})
            self.me = vrcpy.currentuser.CurrentUser(self, resp["data"])
            self._logged_in = True
        except ClientErrors.MfaRequired:
            if mfa is None:
                raise ClientErrors.MfaRequired("Account login requires mfa")
            else:
                await self.verify_mfa(mfa)
                await self.fetch_me()

        await self._pre_loop()

    async def login_auth_token(self, token: str):
        """
        Logs in to vrchat with a pre-existing auth cooke/token
        
        Arguments
        ----------
        token: :class:`str`
            Pre-existing auth token to login with
        """

        logging.debug("Doing logon with pre-existing auth token")

        # Create a session and get api_key
        await self.fetch_system_time()
        self.request.session.cookie_jar.update_cookies([["auth", token]])

        try:
            resp = await self.request.get("/auth")
        except ClientErrors.MissingCredentials:
            raise ClientErrors.InvalidAuthToken(
                "Passed auth token is not valid")

        if not resp["data"]["ok"]:
            raise ClientErrors.InvalidAuthToken(
                "Passed auth token is not valid")

        self._logged_in = True
        await self.fetch_me()
        await self._pre_loop()

    async def verify_mfa(self, mfa: str):
        """
        Used to verify auth token on 2fa enabled accounts
        This is called automatically by :func:`Client.login` when mfa kwarg is passed
        Arguments
        ----------
        mfa: :class:`str`
            One Time Password (OTP, recovery code) or Temporary One Time Password (TOTP, MFA code) to verify auth cookie
        """

        logging.debug("Verifying MFA authtoken")

        if type(mfa) is not str or not (len(mfa) == 6 or len(mfa) == 8):
            raise ClientErrors.MfaInvalid(
                "{} is not a valid MFA code".format(mfa))

        resp = await self.request.post("/auth/twofactorauth/{}/verify".format(
            "totp" if len(mfa) == 6 else "otp"
        ), json={"code": mfa})

        if not resp["data"]["verified"]:
            raise ClientErrors.MfaInvalid(f"{mfa} is not a valid MFA code")

        self._logged_in = True

    @auth_required
    async def logout(self, unauth=True):
        """
        Closes client session and logs out of VRChat
        Keyword Arguments
        ------------------
        unauth: :class:`bool`
            If the auth cookie should be un-authenticated/destroyed.
            Defaults to ``True``
        """

        logging.debug("Doing logout (%sdeauthing authtoken)" % (
            "" if unauth else "not "))

        self.me = None
        self._logout_intent = True

        if unauth:
            # Sending json with this makes it not 401 for some reason
            # Hey, works for me
            await self.request.put("/logout", json={})

        if self.ws is not None:
            await self.ws.close()

        await self.request.close_session()
        await asyncio.sleep(0)

    @auth_required
    async def verify_auth(self) -> Dict[str, Union[bool, str]]:
        """Fetches auth verification status"""
        logging.debug("Verifying auth token")

        resp = await self.request.get("/auth")
        return resp["data"]

    @auth_required
    async def user_exists(
        self, email: str = None, display_name: str = None, id: str = None,
        exclude_id: str = None) -> bool:
        """
        At least one of the kwargs excluding `exclude_id` must be passed
        Checks if a user exists based off their:
            - email
            - display name
            - id

        Keyword Arguments
        ------------------
        email: :class:`str`
            Email to check
        display_name: :class:`str`
            Display name to check
        id: :class:`str`
            User ID to check
        exclude_id: :class:`str`
            User ID to exclude from results
        """

        names = {
            "email": email,
            "displayName": display_name,
            "userId": id,
            "excludeUserId": exclude_id
        }

        req = {}

        all_none = True
        for param in names:
            if names[param] is not None:
                if param in ["email", "displayName", "userId"]:
                    all_none = False
                req[param] = names[param]

        if all_none:
            raise TypeError(
                "You must pass at least one kwarg! (email, display_name, id)")

        resp = await self.request.get("/auth/exists", params=req)
        return resp["data"]["userExists"]

    # Event stuff

    async def start_ws_loop(self):
        while not self._logout_intent:
            auth = await self.fetch_auth_cookie()
            auth = auth["token"]

            self.ws = await self.request.session.ws_connect(
                "wss://pipeline.vrchat.cloud/?authToken="+auth)

            self.loop.create_task(self.on_connect())

            async for message in self.ws:
                message = self.loop.run_in_executor(None, message.json)
                content = self.loop.run_in_executor(
                    None, lambda: json.loads(message["content"]))

                logging.debug("Got ws message (%s)" % message["type"])
                for event in self._event_listeners:
                    if asyncio.iscoroutine(event):
                        self.loop.create_task(event(message, content))
                    else:
                        ThreadWrap(event, message, content)

                switch = {
                    "friend-online": self._on_friend_online,
                    "friend-offline": self._on_friend_offline,
                    "friend-active": self._on_friend_active,
                    "friend-add": self._on_friend_add,
                    "friend-update": self._on_friend_update,
                    "friend-location": self._on_friend_location,
                    "notification": self._on_notification_received,
                    "see-notification": self._on_notification_seen,
                    "response-notification": self._on_notification_response
                }

                if message["type"] in switch:
                    self.loop.create_task(switch[message["type"]](content))


            self.loop.create_task(self.on_disconnect())

    def event(self, func: Callable):
        """
        Decorator that overwrites class ws event hooks.
        Example::
            @client.event
            def on_connect():
                print("Connected to wss pipeline.")

        Arguments
        ----------
        func: `method`
            Event function to register as event hook
        """

        if func.__name__.startswith("on_") and hasattr(self, func.__name__):
            if not asyncio.iscoroutine(func):
                raise ClientErrors.InvalidEventFunction(
                    "'{}' event must be a coroutine!".format(func.__name__))

            logging.debug("Replacing %s via decorator" % func.__name__)
            setattr(self, func.__name__, func)
            return func

        raise ClientErrors.InvalidEventFunction(
            "{} is not a valid event".format(func.__name__))

    def add_listener(self, func: Callable):
        """
        Adds a listener that gets called whenever receiving a websocket event
        Listeners added through this get called before any in-built event

        Arguments
        ----------
        func: `Method`
            Async or Sync method to call when received an event
        """
        self._event_listeners.append(func)

    def remove_listener(self, func: Callable):
        """
        Removes a listener previously added with :func:`Client.add_listener`

        Arguments
        ----------
        func: `Method`
            Previously added method
        """
        self._event_listeners.remove(func)


    async def on_connect(self):
        """
        Called when connected to event websocket
        This can be called multiple times due to vrchat disconnects
        """
        pass

    async def on_disconnect(self):
        """
        Called when disconnected to event websocket
        This can be called multiple times due to vrchat disconnects
        """
        pass

    async def on_ready(self):
        """
        Called when cache has been filled
        """
        pass

    async def _on_friend_online(self, obj):
        user = User(self, obj["user"])
        old_user = self.get_user(user.id)

        self.users.remove(old_user)
        self.users.append(user)

        await self.on_friend_online(old_user, user)

    async def on_friend_online(
        self, before: Union[LimitedUser, User], after: User):
        """
        Called when a friend comes online
        
        Arguments
        ----------
        before: :class:`vrcpy.user.User` OR :class:`vrcpy.limiteduser.LimitedUser`
            Friend object before they came online
        after: :class:`vrcpy.user.User`
            Friend object after they came online
        """
        pass

    async def _on_friend_active(self, obj):
        user = User(self, obj["user"])
        old_user = self.get_user(user.id)

        self.users.remove(old_user)
        self.users.append(user)

        await self.on_friend_active(old_user, user)

    async def on_friend_active(
        self, before: Union[LimitedUser, User], after: User):
        """
        Called when a friend becomes active
        
        Arguments
        ----------
        before: :class:`vrcpy.user.User` OR :class:`vrcpy.limiteduser.LimitedUser`
            Friend object before they went active
        after: :class:`vrcpy.user.User`
            Friend object after they went active
        """
        pass

    async def _on_friend_offline(self, obj):
        user = await self.fetch_user(obj["userId"])
        old_user = self.get_user(user.id)

        self.users.remove(old_user)
        self.users.append(user)

        await self.on_friend_offline(old_user, user)

    async def on_friend_offline(
        self, before: Union[LimitedUser, User], after: User):
        """
        Called when a friend goes offline
        
        Arguments
        ----------
        before: :class:`vrcpy.user.User` OR :class:`vrcpy.limiteduser.LimitedUser`
            Friend object before they went offline
        after: :class:`vrcpy.user.User`
            Friend object after they went offline
        """
        pass

    async def _on_friend_add(self, obj):
        user = User(self, obj["user"])
        self.users.append(user)

        await self.on_friend_add(user)

    async def on_friend_add(self, friend: User):
        """
        Called when a user is added as a friend

        Arguments
        ----------
        friend: :class:`vrcpy.user.User`
        """
        pass

    async def _on_friend_delete(self, obj):
        user = self.get_user(obj["userId"])
        self.users.remove(user)

        await self.on_friend_delete(user)

    async def on_friend_delete(self, friend: User):
        """
        Called when a user is unfriended

        Arguments
        ----------
        friend: :class:`vrcpy.user.User`
        """
        pass

    async def _on_friend_update(self, obj):
        old_user = self.get_user(obj["userId"])
        user = User(self, obj["user"])

        self.users.remove(old_user)
        self.users.append(user)

        await self.on_friend_update(old_user, user)

    async def on_friend_update(self, before: User, after: User):
        """
        Called when a friend updates their profile
        
        Arguments
        ----------
        before: :class:`vrcpy.user.User` OR :class:`vrcpy.limiteduser.LimitedUser`
            Friend object before they updated
        after: :class:`vrcpy.user.User`
            Friend object after they updated
        """
        pass

    async def _on_friend_location(self, obj):
        user = User(self, obj["user"])
        world = World(self, obj["world"])
        
        self.users.remove(self.get_user(obj["userId"]))
        self.users.append(user)

        await self.on_friend_location(user, world, obj["location"])

    async def on_friend_location(
        self, friend: User, world: World, location: str):
        """
        Called when a friend changes location

        Arguments
        ----------
        friend: :class:`vrcpy.user.User`
            Friend that changed location
        world: :class:`vrcpy.world.World`
            World the friend changed to
        location: :class:`str`
            Location ID of the instance friend is in
        """
        pass

    async def _on_notification_received(self, obj):
        await self.on_notification_received(
            Notification(self, obj))

    async def on_notification_received(self, notification: Notification):
        """
        Called when you receive a notification

        Arguments
        ----------
        notification: :class:`vrcpy.notification.Notification`
            Notification you received
        """
        pass

    async def _on_notification_seen(self, obj):
        notif = await self.me.fetch_notification(obj)
        await self.on_notification_seen(notif)

    async def on_notification_seen(self, notification: Notification):
        """
        Called when you mark a notification as seen

        Arguments
        ----------
        notification: :class:`vrcpy.notification.Notification`
            Notification you marked as seen
        """
        pass

    async def _on_notification_response(self, obj):
        notif = await self.me.fetch_notification(obj["notificationId"])
        sender = self.get_user(obj["receiverId"])
        response = await self.me.fetch_notification(obj["responseId"])

        if sender is None:
            sender = await self.fetch_user(obj["receiverId"])

        await self.on_notification_response(
            notif, response, sender)

    async def on_notification_response(
        self, notification: Notification,
        response: Notification, sender: Union[LimitedUser, User]):
        """
        Called when you get a response to a notification you sent

        Arguments
        ----------
        notification: :class:`vrcpy.notification.Notification`
            The original notification you sent
        response: :class:`vrcpy.notification.Notification`
            The response notification
        sender: :class:`vrcpy.user.User` OR :class:`vrcpy.limiteduser.LimitedUser`
            The user that sent the response
        """
        pass