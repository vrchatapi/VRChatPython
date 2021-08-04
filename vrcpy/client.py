from vrcpy.request import Request
from vrcpy.errors import ClientErrors

from vrcpy.user import LimitedUser, User, CurrentUser
from vrcpy.world import LimitedWorld, World, Instance
from vrcpy.avatar import Avatar

from vrcpy.favorite import BaseFavorite
from vrcpy.permission import BasePermission
from vrcpy.file import FileBase
from vrcpy.moderation import PlayerModeration

from vrcpy.notification import InviteNotification, RequestInviteNotification
from vrcpy.notification import FriendRequestNotification, BaseNotification

import vrcpy.enum
import vrcpy.util
import logging
import asyncio
import base64
import json


class Client:
    # Refs to avoid circular imports
    _LimitedUser = LimitedUser
    _User = User
    _CurrentUser = CurrentUser

    _LimitedWorld = LimitedWorld
    _World = World
    _Instance = Instance

    _Avatar = Avatar

    _InviteNotification = InviteNotification
    _RequestInviteNotification = RequestInviteNotification
    _FriendRequestNotification = FriendRequestNotification

    _BaseFavorite = BaseFavorite
    _PlayerModeration = PlayerModeration
    _BasePermission = BasePermission
    _FileBase = FileBase

    def __init__(self, loop=None, verify=True):
        self.request = Request(loop, verify=verify)
        self.me = None

        '''
        Each is a list of LimitedUser objects
        It slowly gets made each a list of User objects via ws events
        You can force all User objects from the start using
            await client.upgrade_friends()
        In "on_ready" event or after
        '''
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
            vrcpy.util.auto_page_coro,
            self.me.fetch_friends,
            task_name="online",
            offline=False))

        tasks.append(vrcpy.util.TaskWrapReturn(
            self.loop,
            vrcpy.util.auto_page_coro,
            self.me.fetch_friends,
            task_name="offline",
            offline=True))

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
                "wss://pipeline.vrchat.cloud/?authToken="+auth,
                proxy=self.request.proxy)

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

    def _remove_authorization_header(self):
        if hasattr(self.request.session, "headers"):
            if "Authorization" in self.request.session.headers:
                del self.request.session.headers["Authorization"]

    # -- Get

    def get_friend(self, id):
        '''
        Gets a cached friend
        May be LimitedUser or User
            id, str
            ID of the user to get
        '''

        logging.debug("Getting cached friend with id " + id)

        for state in self.friends:
            for user in self.friends[state]:
                if user.id == id:
                    return user

        return None

    def get_online_friends(self):
        logging.debug("Getting cached online friends")
        return self.friends["online"]

    def get_active_friends(self):
        logging.debug("Getting cached active friends")
        return self.friends["active"]

    def get_offline_friends(self):
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
        logging.debug("Getting cached favorite friends")
        return self.favorites["friends"]

    def get_favorite_worlds(self, id):
        logging.debug("Getting cached favorite worlds")
        return self.favorites["worlds"]

    def get_favorite_avatars(self, id):
        logging.debug("Getting cached favorite avatars")
        return self.favorites["avatars"]

    # -- Fetch

    async def fetch_me(self):
        '''
        Gets new CurrentUser object
        '''

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
        '''
        Gets a non-cached friend
        Returns a User object
            id, str
            ID of the user to get
        '''

        logging.debug("Getting user via id " + id)

        user = await self.request.get("/users/" + id)
        return User(self, user["data"], loop=self.loop)

    async def fetch_instance(self, world_id, instance_id):
        '''
        Gets instance object
            world_id, str
            ID of the world of the instance
            instance_id, str
            ID of the specific instance
        '''

        logging.debug("Getting instance %s:%s" % (world_id, instance_id))

        instance = await self.request.get(
            "/worlds/%s/%s" % (world_id, instance_id))
        return Instance(self, instance["data"], self.loop)

    async def fetch_world(self, world_id):
        '''
        Gets world object by ID
            world_id, str
            ID of the world to fetch
        '''

        logging.debug("Getting world of id " + world_id)

        world = await self.request.get("/worlds/"+world_id)
        return World(self, world["data"], self.loop)

    async def fetch_avatar(self, avatar_id):
        '''
        Fetches avatar via ID
        returns Avatar object
            avatar_id, str
            ID of avatar to fetch
        '''

        logging.debug("Fetching avatar " + avatar_id)

        avatar = await self.request.get("/avatars/" + avatar_id)
        return Avatar(self, avatar["data"], self.loop)

    async def upgrade_friends(self):
        '''
        Forces all client.friends LimitedUser objects
        to become User objects
        '''

        tasks = []
        for state in self.friends:
            for user in self.friends[state]:
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
        logging.debug("Fetching auth cookie")

        data = await self.request.get("/auth")
        return data["data"]

    async def fetch_system_time(self):
        logging.debug("Fetching system time")

        data = await self.request.get("/time")
        return data["data"]

    async def fetch_online_user_count(self):
        logging.debug("Fetching online user count")

        data = await self.request.get("/visits")
        return data["data"]

    # Main

    async def login(self, username, password, mfa=None):
        '''
        Login to VRChat

        username, string
            Username/email of VRC account
        password, string
            Password of VRC account
        
        Optional:
            mfa, string
            TOTP or OTP code to verify authtoken
        '''

        b64 = base64.b64encode((username+":"+password).encode()).decode()

        resp = await self.request.get("/auth/user", headers={"Authorization": "Basic "+b64})
        if "requiresTwoFactorAuth" in resp["data"]:
            if mfa is None:
                raise ClientErrors.MfaRequired("Account login requires mfa")
            else:
                await self.verify_mfa(mfa)
                await self.fetch_me()
        else:
            self.me = CurrentUser(self, resp["data"], self.loop)

        await self._pre_loop()

    async def login_auth_token(self):
        pass

    async def verify_mfa(self, mfa: str):
        '''
        Used to verify authtoken on 2fa enabled accounts
            mfa, string
            2FactorAuth code (totp or otp)
        '''

        logging.debug("Verifying MFA authtoken")

        if type(mfa) is not str or not (len(mfa) == 6 or len(mfa) == 8):
            raise ClientErrors.MfaInvalid("{} is not a valid MFA code".format(mfa))

        await self.request.post("/auth/twofactorauth/{}/verify".format(
            "totp" if len(mfa) == 6 else "otp"
        ), json={"code": mfa})

    async def logout(self, unauth=True):
        '''
        Closes client session and logs out VRC user
            unauth, bool
            If should unauth the session cookie
        '''

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
        '''
        Automates login+start
        This function is blocking

        username, string
            Username/email of VRC account
        password, string
            Password of VRC account
        
        Optional:
            mfa, string
            TOTP or OTP code to verify authtoken
        '''

        async def run():
            await self.login(username, password, mfa)
            await self.start()

        self.loop.run_until_complete(run())
        self.loop.run_until_complete(self.logout())

    # Websocket Stuff

    async def start(self):
        '''
        Starts the ws event _ws_loop
        This function is blocking
        '''

        logging.debug("Starting ws loop")

        await self._ws_loop()

    def event(self, func):
        '''
        Decorator that overwrites class ws event hooks
        Example
        --------
        @client.event
        def on_connect():
            print("Connected to wss pipeline.")
        '''

        if func.__name__.startswith("on_") and hasattr(self, func.__name__):
            logging.debug("Replacing %s via decorator" % func.__name__)
            setattr(self, func.__name__, func)
            return func

        raise ClientErrors.InvalidEventFunction(
            "{} is not a valid event".format(func.__name__))

    async def on_connect(self):
        # Called at the start of ws event loop
        pass

    async def on_ready(self):
        # Called when cache is finished
        pass

    async def on_disconnect(self):
        # Called at the end of ws event loop
        pass

    async def _on_friend_online(self, obj):
        user = User(self, obj["user"], self.loop)
        self._remove_friend_from_cache(user.id)

        self.friends["online"].append(user)

        await self.on_friend_online(user)

    async def on_friend_online(self, friend):
        # Called when a friend comes online
        pass

    async def _on_friend_offline(self, obj):
        user = await self.fetch_user(obj["userId"])
        self._remove_friend_from_cache(user.id)
        self.friends["offline"].append(user)

        await self.on_friend_offline(user)

    async def on_friend_offline(self, friend):
        # Called when a friend goes offline
        pass

    async def _on_friend_active(self, obj):
        user = User(self, obj["user"], self.loop)
        self._remove_friend_from_cache(user.id)
        self.friends["active"].append(user)

        await self.on_friend_active(user)

    async def on_friend_active(self, friend):
        # Called when a friend becomes active
        pass

    async def _on_friend_add(self, obj):
        user = User(self, obj["user"], self.loop)
        self._remove_friend_from_cache(user.id)
        self.friends[user.state].append(user)

        await self.on_friend_add(user)

    async def on_friend_add(self, friend):
        # Called when a new friend is added to your account
        pass

    async def _on_friend_delete(self, obj):
        user = await self.fetch_user(obj["userId"])
        self._remove_friend_from_cache(user.id)

        await self.on_friend_delete(user)

    async def on_friend_delete(self, friend):
        # Called when a friend is unfriended
        pass

    async def _on_friend_update(self, obj):
        user = User(self, obj["user"], self.loop)
        ouser = self.get_friend(user.id)
        self._remove_friend_from_cache(user.id)
        self.friends[user.state].append(user)

        await self.on_friend_update(ouser, user)

    async def on_friend_update(self, before, after):
        '''
        Called when a friend makes an update to their profile
            before, User
            User before they updated their profile
            after, User
            User after they updated their profile
        '''
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
        '''
        Called when a friend changes location
            before, User
            User before they changed location
            after, User
            User after they changed location
        '''
        pass

    async def _on_notification(self, obj):
        notif = BaseNotification.build_notification(
            self, obj["data"], self.loop)

        await self.on_notification(notif)

    async def on_notification(self, notification):
        # Called when recieved a notification
        pass