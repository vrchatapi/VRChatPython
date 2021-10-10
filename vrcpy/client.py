﻿from .errors import ClientErrors
from .http import Request

from .util.threadwrap import ThreadWrap
from .notification import Notification
from .decorators import auth_required
from .currentuser import CurrentUser
from .limiteduser import LimitedUser
from .config import Config
from .world import World
from .user import User

from .types.enum import DeveloperType
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
    loop: :class:`vrcpy.AbstractEventLoop`
        Event loop client will create new asyncio tasks in.
    me: :class:`vrcpy.currentuser.CurrentUser`
        Last fetched user profile object
    request: :class:`vrcpy.http.Request`
        Internal AIOHTTP Wrapper instance
    users: :class:`list`
        User cache
    ws: :class:`aiohttp.WebSocketResponse`
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
    async def fetch_me(self) -> CurrentUser:
        """
        Fetches new CurrentUser object.
        This also updates `Client.me`
        """

        logging.debug("Fetching CurrentUser")

        me = await self.request.get("/auth/user")
        me = CurrentUser(self, me["data"])

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
            self.me = CurrentUser(self, resp["data"])
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
        This is called automatically by `Client.login` when mfa kwarg is passed
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

    async def _ws_loop(self):
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
        Removes a listener previously added with :method:`vrcpy.client.Client.add_listener`

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

    async def on_friend_unfriend(self, friend: User):
        """
        Called when a user is added as a friend

        Arguments
        ----------
        friend: :class:`vrcpy.user.User` OR :class:`vrcpy.limiteduser.LimitedUser`
            Friend object before they were unfriended
        """

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

        Arugments
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