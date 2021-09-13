from vrcpy.request import Request
from vrcpy.errors import ClientErrors

from vrcpy.user import User, CurrentUser
from vrcpy.world import World, Instance
from vrcpy.avatar import Avatar

from vrcpy.notification import BaseNotification

import vrcpy.enum
import vrcpy.util
import logging
import asyncio
import base64
import json


class Client:
    """
    VRChat Client object used to interact with the VRChat API

    Keyword Arguments
    ------------------
    loop: :class:`asyncio.AbstractEventLoop`
        Event loop client will create new asyncio tasks in.
        Defaults to ``None``
    verify: :class:`bool`
        If aiohttp should verify ssl certificates when making requests.
        Defaults to ``True``

    Attributes
    -----------
    favorites: :class:`dict`
        Dictionary containing cached :class:`vrcpy.FavoriteGroup` objects
        It is structured like so::

            Client.favorites = {
                vrcpy.enum.FavoriteType.WORLD: [],
                vrcpy.enum.FavoriteType.FRIEND: [],
                vrcpy.enum.FavoriteType.AVATAR: []
            }
    friends: :class:`dict`
        Dictionary containing cached friends.
        It is structured like so::

            Client.friends = {
                "online": [],
                "active": [],
                "offline": []
            }
    logout_intent: :class:`bool`
        Describes if websocket had intent to disconnect
        Is used for websocket reconnect logic
    loop: :class:`asyncio.AbstractEventLoop`
        Event loop used to run asyncio tasks
    me: :class:`vrcpy.CurrentUser`
        Logged in user
    ws: :class:`aiohttp.WebSocketResponse`
        Websocket connection to VRChat
    """


    def __init__(self, loop=None, verify=True):
        self.request = Request(loop, verify=verify)
        self.me = None

        self.friends = {
            "online": [],
            "active": [],
            "offline": []
        }

        self.favorites = {
            vrcpy.enum.FavoriteType.WORLD: [],
            vrcpy.enum.FavoriteType.FRIEND: [],
            vrcpy.enum.FavoriteType.AVATAR: []
        }

        self.ws = None
        self.loop = loop or asyncio.get_event_loop()
        self.logout_intent = False

        if loop is not None:
            asyncio.set_event_loop(loop)

    async def _pre_loop(self):
        tasks = []
        await self.me.fetch_all_favorites()

        # Fetch all friends
        tasks.append(vrcpy.util.TaskWrapReturn(
            self.loop,
            vrcpy.util.full_paginate,
            self.me.fetch_friends,
            task_name="online",
            offline=True
        ))

        tasks.append(vrcpy.util.TaskWrapReturn(
            self.loop,
            vrcpy.util.full_paginate,
            self.me.fetch_friends,
            task_name="offline",
            offline=False
        ))

        for friend in self.me.active_friends:
            tasks.append(vrcpy.util.TaskWrapReturn(
                self.loop, self.fetch_user, friend, task_name="active"))

        for task in tasks:
            await task.task
            if type(task.returns) is not list:
                self.friends[task.name].append(task.returns)
            else:
                self.friends[task.name] = task.returns

        del tasks
        self.loop.create_task(self.on_ready())

    async def _ws_loop(self):
        while not self.logout_intent:
            auth = await self.fetch_auth_cookie()
            auth = auth["token"]

            self.ws = await self.request.session.ws_connect(
                "wss://pipeline.vrchat.cloud/?authToken="+auth)

            self.loop.create_task(self.on_connect())

            async for message in self.ws:
                message = message.json()
                content = json.loads(message["content"])

                logging.debug("Got ws message (%s)" % message["type"])

                switch = {
                    "friend-location": self._on_friend_location,
                    "friend-online": self._on_friend_online,
                    "friend-offline": self._on_friend_offline,
                    "friend-active": self._on_friend_active,
                    "friend-add": self._on_friend_add,
                    "friend-delete": self._on_friend_delete,
                    "friend-update": self._on_friend_update,
                    "notification": self._on_notification
                }

                if message["type"] in switch:
                    self.loop.create_task(switch[message["type"]](content))

        self.loop.create_task(self.on_disconnect())

    # -- Get

    def get_friend(self, id):
        """
        Gets a cached friend, which may return as a :class:`LimitedUser` or :class:`User`
        Returns ``None`` if no user with given id is found
        
        Arguments
        -----------
        id: :class:`str`
            User ID of the friend to fetch
        """

        logging.debug("Getting cached friend with id " + id)

        for state in self.friends:
            for user in self.friends[state]:
                if user.id == id:
                    return user

        return None

    def get_online_friends(self):
        """Gets cached online friends as a :class:`list`"""

        logging.debug("Getting cached online friends")
        return self.friends["online"]

    def get_active_friends(self):
        """Gets cached active friends as a :class:`list`"""

        logging.debug("Getting cached active friends")
        return self.friends["active"]

    def get_offline_friends(self):
        """Gets cached offline friends as a :class:`list`"""

        logging.debug("Getting cached offline friends")
        return self.friends["offline"]

    def _remove_friend_from_cache(self, id):
        user_state = ""
        for state in self.friends:
            for user in self.friends[state]:
                if user.id == id:
                    user_state = state
                    break

            if user_state == state:
                break

        if user_state == "":
            return

        self.friends[user_state].remove(self.get_friend(id))
        logging.debug("Removed friend %s from cache" % id)

    def get_favorite_friends(self, id):
        """Gets cached favorite friends as a :class:`list`"""

        logging.debug("Getting cached favorite friends")
        return self.favorites[vrcpy.enum.FavoriteType.FRIEND]

    def get_favorite_worlds(self, id):
        """Gets cached favorite worlds as a :class:`list`"""

        logging.debug("Getting cached favorite worlds")
        return self.favorites[vrcpy.enum.FavoriteType.WORLD]

    def get_favorite_avatars(self, id):
        """Gets cached favorite avatars as a :class:`list`"""

        logging.debug("Getting cached favorite avatars")
        return self.favorites[vrcpy.enum.FavoriteType.AVATAR]

    # -- Fetch

    async def fetch_me(self):
        """Fetches new CurrentUser object. This also updates `Client.me`"""

        logging.debug("Fetching me")

        me = await self.request.get("/auth/user")
        me = CurrentUser(
            self,
            me["data"],
            loop=self.loop
        )

        self.me = me
        return me

    async def fetch_user(self, id):
        """
        Fetches a non-cached user, and returns as a :class:`vrcpy.User` object
        
        Arguments
        ----------
        id: :class:`str`
            ID of the use to fetch
        """

        logging.debug("Getting user via id " + id)

        user = await self.request.get("/users/" + id)
        return User(self, user["data"], loop=self.loop)

    async def fetch_instance(self, world_id, instance_id):
        """
        Fetches a world instance, returns :class:`vrcpy.Instance`

        Arguments
        ----------
        world_id: :class:`str`
            ID of the instance world
        instance_id: :class:`str`
            ID of instance
        """

        logging.debug("Getting instance %s:%s" % (world_id, instance_id))

        instance = await self.request.get(
            "/worlds/%s/%s" % (world_id, instance_id))
        return Instance(self, instance["data"], self.loop)

    async def fetch_world(self, world_id):
        """
        Fetches a world, returns :class:`vrcpy.World`
        
        Arguments
        ----------
        world_id: :class:`str`
            ID of the world to fetch
        """

        logging.debug("Getting world of id " + world_id)

        world = await self.request.get("/worlds/"+world_id)
        return World(self, world["data"], self.loop)

    async def fetch_avatar(self, avatar_id):
        """
        Fetches an avatar, returns as :class:`vrcpy.Avatar`

        Arguments
        ----------
        avatar_id: :class:`str`
            ID of avatar to fetch
        """

        logging.debug("Fetching avatar " + avatar_id)

        avatar = await self.request.get("/avatars/" + avatar_id)
        return Avatar(self, avatar["data"], self.loop)

    async def upgrade_friends(self):
        """
        Forces all Client.friends :class:`LimitedUser` objects to become :class:`User` objects

        .. warning::
            This calls `LimitedUser.fetch_full()` on every cached :class:`LimitedUser` friend!
            If user has large number of friends this could flood VRChat servers and you could get rate limited!
        """

        tasks = []
        for state in self.friends:
            for user in self.friends[state]:
                if type(user) is not User:
                    tasks.append(vrcpy.util.TaskWrapReturn(
                        self.loop,
                        user.fetch_full,
                        task_name=state
                    ))

        self.friends = {"online": [], "active": [], "offline": []}

        for task in tasks:
            await task.task
            self.friends[task.returns.state].append(task.returns)

        logging.debug("Finished upgrading friends")

    # -- Misc

    async def fetch_auth_cookie(self):
        """Fetches current session authentication cookie"""
        logging.debug("Fetching auth cookie")

        data = await self.request.get("/auth")
        return data["data"]

    async def fetch_system_time(self):
        """Fetches current VRChat system time"""
        logging.debug("Fetching system time")

        data = await self.request.get("/time")
        return data["data"]

    async def fetch_online_user_count(self) -> int:
        """Fetches current users online in VRChat"""
        logging.debug("Fetching online user count")

        data = await self.request.get("/visits")
        return data["data"]

    async def fetch_system_health(self):
        """Fetches vrchat system heatlh
        
        {
            "ok": bool,
            "server_name": str,
            "build_version_tag": str
        }
        """
        logging.debug("Fetching system health")

        data = await self.request.get("/health")

        # Change to a more python nameing scheme :)
        data["server_name"] = data["serverName"]
        data["build_version_tag"] = data["buildVersionTag"]
        del data["serverName"]
        del data["buildVersionTag"]

        return data

    # Main

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
            One Time Password (OTP, recovery code) or Temporary One Time Password (TOTP, MFA code) to verify auth cookie
        """

        b64 = base64.b64encode((username+":"+password).encode()).decode()

        try:
            resp = await self.request.get("/auth/user", headers={"Authorization": "Basic "+b64})
            self.me = CurrentUser(self, resp["data"], self.loop)
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
            raise ClientErrors.MfaInvalid("{} is not a valid MFA code".format(mfa))

        resp = await self.request.post("/auth/twofactorauth/{}/verify".format(
            "totp" if len(mfa) == 6 else "otp"
        ), json={"code": mfa})

        if not resp["data"]["verified"]:
            raise ClientErrors.MfaInvalid(f"{mfa} is not a valid MFA code")

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
        self.friends = {
            "online": [],
            "active": [],
            "offline": []
        }
        self.favorites = {
            vrcpy.enum.FavoriteType.WORLD: [],
            vrcpy.enum.FavoriteType.FRIEND: [],
            vrcpy.enum.FavoriteType.AVATAR: []
        }

        if unauth:
            # Sending json with this makes it not 401 for some reason
            # Hey, works for me
            await self.request.put("/logout", json={})

        await self.request.close_session()

        if self.ws is not None:
            await self.ws.close()

        await asyncio.sleep(0)

    def run(self, username, password, mfa=None):
        """
        Automates login+start
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
            One Time Password (OTP, recovery code) or Temporary One Time Password (TOTP, MFA code) to verify auth cookie
        """

        async def run():
            await self.login(username, password, mfa)
            await self.start()

        try:
            self.loop.run_until_complete(run())
        except KeyboardInterrupt as e:
            self.loop.run_until_complete(self.logout())
        except Exception as e:
            self.loop.run_until_complete(self.logout())
            raise e.__class__(str(e))

    # Websocket Stuff

    async def start(self):
        """
        Starts the websocket event loop
        This funtion is blocking
        """

        logging.debug("Starting ws loop")

        await self._ws_loop()

    def event(self, func):
        """
        Decorator that overwrites class ws event hooks.
        Example::

            @client.event
            def on_connect():
                print("Connected to wss pipeline.")
        """

        if func.__name__.startswith("on_") and hasattr(self, func.__name__):
            logging.debug("Replacing %s via decorator" % func.__name__)
            setattr(self, func.__name__, func)
            return func

        raise ClientErrors.InvalidEventFunction(
            "{} is not a valid event".format(func.__name__))

    async def on_connect(self):
        """Called at the start of ws event loop"""
        pass

    async def on_ready(self):
        """Called when cache is finished"""
        pass

    async def on_disconnect(self):
        """Called at the end of ws event loop"""
        pass

    async def _on_friend_online(self, obj):
        user = User(self, obj["user"], self.loop)
        self._remove_friend_from_cache(user.id)

        self.friends["online"].append(user)

        await self.on_friend_online(user)

    async def on_friend_online(self, friend):
        """
        Called when a friend comes online
        
        Arguments
        ----------
        friend: :class:`vrcpy.User`
        """
        pass

    async def _on_friend_offline(self, obj):
        user = await self.fetch_user(obj["userId"])
        self._remove_friend_from_cache(user.id)
        self.friends["offline"].append(user)

        await self.on_friend_offline(user)

    async def on_friend_offline(self, friend):
        """Called when a friend goes offline
        
        Arguments
        ----------
        friend: :class:`vrcpy.User`"""
        pass

    async def _on_friend_active(self, obj):
        user = User(self, obj["user"], self.loop)
        self._remove_friend_from_cache(user.id)
        self.friends["active"].append(user)

        await self.on_friend_active(user)

    async def on_friend_active(self, friend):
        """Called when a friend becomes active
        
        Arguments
        ----------
        friend: :class:`vrcpy.User`"""
        pass

    async def _on_friend_add(self, obj):
        user = User(self, obj["user"], self.loop)
        self._remove_friend_from_cache(user.id)
        self.friends[user.state].append(user)

        await self.on_friend_add(user)

    async def on_friend_add(self, friend):
        """Called when a new friend is added to your account
        
        Arguments
        ----------
        friend: :class:`vrcpy.User`"""
        pass

    async def _on_friend_delete(self, obj):
        user = await self.fetch_user(obj["userId"])
        self._remove_friend_from_cache(user.id)

        await self.on_friend_delete(user)

    async def on_friend_delete(self, friend):
        """Called when a friend is unfriended
        
        Arguments
        ----------
        friend: :class:`vrcpy.User`"""
        pass

    async def _on_friend_update(self, obj):
        user = User(self, obj["user"], self.loop)
        ouser = self.get_friend(user.id)
        self._remove_friend_from_cache(user.id)
        self.friends[user.state].append(user)

        await self.on_friend_update(ouser, user)

    async def on_friend_update(self, before, after):
        """
        Called when a friend makes an update to their profile
        
        Arguments
        ----------
        before: :class:`vrcpy.User`
            User before they updated their profile
        after: :class:`vrcpy.User`
            User after they updated their profile
        """
        pass

    async def _on_friend_location(self, obj):
        # Add location data
        obj["user"].update({
            "location": obj["location"],
            "instanceId": obj["location"].split(
                ":")[1] if ":" in obj["location"] else obj["location"],
            "worldId": obj["location"].split(
                ":")[0] if ":" in obj["location"] else obj["location"]
        })

        user = User(self, obj["user"], self.loop)
        ouser = self.get_friend(user.id)

        self._remove_friend_from_cache(user.id)
        self.friends[user.state].append(user)

        await self.on_friend_location(ouser, user)

    async def on_friend_location(self, before, after):
        """
        Arguments
        ----------
        before: :class:`vrcpy.User`
            User before they changed location
        after: :class:`vrcpy.User`
            User after they changed location
        """
        pass

    async def _on_notification(self, obj):
        notif = BaseNotification.build_notification(
            self, obj["data"], self.loop)

        await self.on_notification(notif)

    async def on_notification(self, notification):
        """Called when recieved a notification"""
        pass
