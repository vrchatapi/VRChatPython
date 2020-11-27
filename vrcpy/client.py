from vrcpy.request import Request
from vrcpy.errors import ClientErrors

from vrcpy.user import *
from vrcpy.world import *
from vrcpy.notification import *
from vrcpy.favorite import BaseFavorite
from vrcpy.permission import BasePermission
from vrcpy.file import FileBase
from vrcpy.moderation import PlayerModeration

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
    _InviteNotification = InviteNotification
    _RequestInviteNotification = RequestInviteNotification
    _FriendRequestNotification = FriendRequestNotification
    _BaseFavorite = BaseFavorite
    _PlayerModeration = PlayerModeration

    def __init__(self, loop=None, verify=True):
        self.request = Request(verify=verify)

        self.me = None

        '''
        This is a list of LimitedUser objects
        It slowly gets made a list of User objects via ws events
        You can force all User objects from the start using
            await client.upgrade_friends()
        In "on_connect" event or after
        '''

        self.friends = []

        self.ws = None
        self.loop = loop or asyncio.get_event_loop()

        if loop is not None:
            asyncio.set_event_loop(loop)

    async def _ws_loop(self):
        self.friends = await self.me.fetch_friends()
        self.loop.create_task(self.on_connect())

        async for message in self.ws:
            message = message.json()
            content = json.loads(message["content"])

            logging.debug("Got ws message (%s)" % message["type"] )

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

    # Utility

    def get_friend(self, id):
        '''
        Gets a cached friend
        May be LimitedUser or User

            id, str
            ID of the user to get
        '''

        logging.info("Getting cached friend with id " + id)

        for user in self.friends:
            if user.id == id:
                return user

        return None

    async def fetch_user_via_id(self, id):
        '''
        Gets a non-cached friend
        Returns a User object

            id, str
            ID of the user to get
        '''

        logging.info("Getting user via id " + id)

        user = await self.request.call("/users/" + id)
        return User(self, user["data"], loop=self.loop)

    async def fetch_instance_via_id(self, world_id, instance_id):
        '''
        Gets instance object

            world_id, str
            ID of the world of the instance

            instance_id, str
            ID of the specific instance
        '''

        logging.info("Getting instance %s:%s" % (world_id, instance_id))

        instance = await self.request.call("/worlds/%s/%s" % (world_id, instance_id))
        return Instance(self, instance["data"], self.loop)

    async def fetch_permissions(self, condensed=False):
        '''
        Gets users permissions
        Returns list of different Permission objects

            condensed, bool
            Whether to return condensed perms or not
            If this is true then return will be a dict of single key-value pairs
        '''

        logging.info("Getting permissions (%scondensed)" % ("" if condensed else "not "))

        if condensed:
            perms = await self.request.call("/auth/permissions", params={"condensed": True})
            return perms["data"]
        else:
            perms = await self.request.call("/auth/permissions")
            return [BasePermission.build_permission(self, perm, self.loop) for perm in perms["data"]]

    async def get_files(self, tag=None, n=100):
        '''
        Gets user icons
        Returns list of IconFile objects

            tag, str
            Tag to filter files

            n, int
            Number of files to return (max might be 100?)
        '''

        logging.info("Getting files (tag is %s)" % tag)

        params = {"n": n}
        if tag is not None:
            params.update({"tag": tag})

        files = await self.request.call("/files", params=params)
        return [FileBase.build_file(self, file, self.loop) for file in files["data"]]

    async def upgrade_friends(self):
        '''
        Forces all client.friends LimitedUser objects
        to become User objects
        '''

        friends = []

        for friend in self.friends:
            logging.debug("Upgrading " + friend.display_name)
            friends.append(await friend.fetch_full())

        self.friends = friends
        logging.info("Finished upgrading friends")

    # Main

    async def fetch_me(self, **kwargs):
        '''
        Gets new CurrentUser object
        kwargs are extra options to pass to request.call
        '''

        logging.info("Fetching me")

        me = await self.request.call("/auth/user", **kwargs)
        me = CurrentUser(
            self,
            me["data"],
            loop=self.loop
        )

        self.me = me
        return me

    async def login(self, username=None, password=None, b64=None, create_session=True):
        '''
        Used to login as a VRC user

        Must include one of the combinations:
            Username/Password login
                username, string
                Username/email of VRC account

                password, string
                Password of VRC account

            b64 login
                b64, string
                Base64 encoded username:password

        Optional:
            create_session, bool
            Create a new session or not, defaults to True
        '''

        logging.info("Doing logon (%screating new session)" % ("" if not create_session else "not "))

        if b64 is None:
            if username is None or password is None:
                raise ClientErrors.MissingCredentials("Did not pass username+password or b64 for login")

            b64 = base64.b64encode((username+":"+password).encode()).decode()

        resp = await self.request.call(
            "/auth/user",
            headers={"Authorization": "Basic " + b64},
            no_auth=create_session
        )

        cookie = None
        for cookie in resp["response"].headers.getall("Set-Cookie"):
            if "auth=authcookie" in cookie:
                break

        if create_session:
            self.request.new_session(b64)
            self.request.session.cookie_jar.update_cookies(
                [["auth", cookie[5:]]]
            )

        if "requiresTwoFactorAuth" in resp["data"]:
            raise ClientErrors.MfaRequired("Account login requires 2fa")

        self._remove_authorization_header()
        self.me = CurrentUser(self, resp["data"], self.loop)

    async def login2fa(self, username=None, password=None, b64=None, mfa=None):
        '''
        Used to login as a VRC user

        Must include one of the combinations:
            Username/Password login
                username, string
                Username/email of VRC account

                password, string
                Password of VRC account

            b64 login
                b64, string
                Base64 encoded username:password

        Optional:
            mfa, string
            TOTP or OTP code to verify authtoken
        '''

        logging.info("Doing 2falogon")

        try:
            await self.login(username, password, b64)
        except ClientErrors.MfaRequired:
            await self.verify2fa(mfa)
            await self.login(username, password, b64, False)

    async def login_auth_token(self, token):
        '''
        Used to login as a VRC user using an existing auth token

            token, str
            Authtoken to login with
        '''

        logging.info("Doing logon with pre-existing auth token")

        self.request.new_session()
        self.request.session.cookie_jar.update_cookies([["auth", token]])

        try:
            resp = await self.request.call("/auth")
        except ClientErrors.MissingCredentials:
            raise ClientErrors.InvalidAuthToken("Passed auth token is not valid")

        if not resp["data"]["ok"]:
            raise ClientErrors.InvalidAuthToken("Passed auth token is not valid")

        await self.fetch_me()

    async def verify2fa(self, mfa):
        '''
        Used to verify authtoken on 2fa enabled accounts

            mfa, string
            2FactorAuth code (totp or otp)
        '''

        logging.info("Verifying 2fa authtoken")

        if type(mfa) is not str:
            raise ClientErrors.MfaInvalid("{} is not a valid 2fa code".format(mfa))

        resp = await self.request.call("/auth/twofactorauth/{}/verify".format(
                "totp" if len(mfa) == 6 else "otp"
            ), "POST", jdict={"code": mfa})

    async def logout(self, unauth=True):
        '''
        Closes client session and logs out VRC user

            unauth, bool
            If should unauth the session cookie
        '''

        logging.info("Doing logout (%sdeauthing authtoken)" % ("" if unauth else "not "))

        self.me = None
        self.friends = None

        if unauth:
            # Sending json with this makes it not 401 for some reason
            # Hey, works for me
            await self.request.call("/logout", "PUT", jdict={})

        await self.request.close_session()

        if self.ws is not None:
            await self.ws.close()

        await asyncio.sleep(0)

    def run(self, username=None, password=None, b64=None, mfa=None, token=None,
            unauth=True):
        '''
        Automates login+start
        This function is blocking

        Must pass one of these combinations of kwargs:
            Username/Password login
                username, string
                Username/email of VRC account

                password, string
                Password of VRC account

                mfa, string, optional
                2FactorAuth code (totp or otp)

            b64 login
                b64, string
                Base64 encoded username:password

                mfa, string, optional
                2FactorAuth code (totp or otp)

            token login
                token, str
                Authtoken to login with

        Can also include:
            unauth, bool
            If should unauth the session cookie
        '''

        try:
            self.loop.run_until_complete(self._run(
                username,
                password,
                b64,
                mfa,
                token
            ))
        except KeyboardInterrupt:
            pass

        self.loop.run_until_complete(self.logout(unauth))

    async def _run(self, username=None, password=None, b64=None, mfa=None, token=None):
        if token is None:
            await self.login2fa(username, password, b64, mfa)
        else:
            await self.login_auth_token(token)

        await self.start()

    # Websocket Stuff

    async def start(self):
        '''
        Starts the ws event _ws_loop
        This function is blocking
        '''

        logging.info("Starting ws loop")

        authToken = ""
        for cookie in self.request.session.cookie_jar:
            if cookie.key == "auth":
                authToken = cookie.value.split(";")[0]

        self.ws = await self.request.session.ws_connect("wss://pipeline.vrchat.cloud/?authToken="+authToken)
        await self._ws_loop()

    async def event(self, func):
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

        raise ClientErrors.InvalidEventFunction("{} is not a valid event".format(func.__name__))

    async def on_connect(self):
        # Called at the start of ws event loop
        pass

    async def on_disconnect(self):
        # Called at the end of ws event loop
        pass

    async def _on_friend_online(self, obj):
        user = User(self, obj["user"], self.loop)
        friend = self.get_friend(user.id)

        if friend is not None:
            self.friends.remove(friend)
        self.friends.append(user)

        await self.on_friend_online(user)

    async def on_friend_online(self, friend):
        # Called when a friend comes online
        pass

    async def _on_friend_offline(self, obj):
        user = await self.fetch_user_via_id(obj["userId"])
        friend = self.get_friend(user.id)

        if friend is not None:
            self.friends.remove(friend)
        self.friends.append(user)

        await self.on_friend_offline(user)

    async def on_friend_offline(self, friend):
        # Called when a friend goes offline
        pass

    async def _on_friend_active(self, obj):
        user = User(self, obj["user"], self.loop)
        friend = self.get_friend(user.id)

        if friend is not None:
            self.friends.remove(friend)
        self.friends.append(user)

        await self.on_friend_active(user)

    async def on_friend_active(self, friend):
        # Called when a friend becomes active
        pass

    async def _on_friend_add(self, obj):
        user = User(self, obj["user"], self.loop)
        friend = self.get_friend(user.id)

        if friend is not None:
            self.friends.remove(friend)
        self.friends.append(user)

        await self.on_friend_add(user)

    async def on_friend_add(self, friend):
        # Called when a new friend is added to your account
        pass

    async def _on_friend_delete(self, obj):
        user = await self.fetch_user_via_id(obj["userId"])
        friend = self.get_friend(user.id)

        if friend is not None:
            self.friends.remove(friend)

        await self.on_friend_delete(user)

    async def on_friend_delete(self, friend):
        # Called when a friend is unfriended
        pass

    async def _on_friend_update(self, obj):
        user = User(self, obj["user"], self.loop)
        ouser = self.get_friend(user.id)

        if ouser is not None:
            self.friends.remove(ouser)
        self.friends.append(user)

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
        user = User(self, obj["user"], self.loop)
        ouser = self.get_friend(user.id)

        if ouser is not None:
            self.friends.remove(ouser)
        self.friends.append(user)

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
        await self.on_notification(obj)

    async def on_notification(self, notification):
        # Called when recieved a notification
        pass
