from vrcpy._hardtyping import *
from vrcpy.request import *
from vrcpy.errors import *
from vrcpy import objects
from vrcpy import aobjects

from datetime import datetime

import urllib
import base64
import time
import json

class Client:

    # Log

    def _log(self, log): # TODO: Finish logging, also, dunno how I'm gonna do this yet
        dt = datetime.now().strftime("%d/%m - %H:%M:%S")

        if self.log_to_console:
            print("[%s] %s" % dt, log)

    # User calls

    def fetch_me(self):
        '''
        Simply returns newest version of CurrentUser
        '''

        resp = self.api.call("/auth/user")
        self._raise_for_status(resp)

        self.me = objects.CurrentUser(self, resp["data"])
        return self.me

    def fetch_full_friends(self, offline=True, n=0, offset=0):
        '''
        Returns list of User objects
        !! This function uses possibly lot of calls, use with caution

            offline, bool
            Include offline friends or not

            n, int
            Number of friends to return (0 for all)

            offset, int
            Skip first <offset> friends
        '''

        lfriends = self.fetch_friends(offline, n, offset)
        friends = []

        # Get friends
        for friend in lfriends:
            time.sleep(0)
            friends.append(friend.fetch_full())

        return friends

    def fetch_friends(self, offline=False, n=0, offset=0):
        '''
        Returns list of LimitedUser objects

            offline, bool
            Get offline friends instead of online friends

            n, int
            Number of friends to return (0 for all)

            offset, int
            Skip first <offset> friends
        '''

        friends = []

        while True:
            newn = 100
            if not n == 0 and n - len(friends) < 100: newn = n - len(friends)

            last_count = 0

            resp = self.api.call("/auth/user/friends", params={"offset": offset, "offline": offline, "n": newn})
            self._raise_for_status(resp)

            for friend in resp["data"]:
                last_count += 1
                friends.append(objects.LimitedUser(self, friend))

            if last_count < 100:
                break

            offset += 100

        return friends

    def fetch_user_by_id(self, id):
        '''
        Returns User object

            id, string
            UserId of the user
        '''

        resp = self.api.call("/users/"+id)
        self._raise_for_status(resp)

        return objects.User(self, resp["data"])

    def fetch_user_by_name(self, name):
        '''
        Returns User object

            name, string
            Name of the user
        '''

        resp = self.api.call("/users/"+urllib.parse.urlencode(name)+"/name")
        self._raise_for_status(resp)

        return objects.User(self, resp["data"])

    # Avatar calls

    def fetch_avatar(self, id):
        '''
        Returns Avatar object

            id, string,
            AvatarId of the avatar
        '''

        resp = self.api.call("/avatars/"+id)
        self._raise_for_status(resp)

        return objects.Avatar(self, resp["data"])

    def list_avatars(self, user: oString = None, featured: oBoolean = None, tag: oString = None,\
        userId: oString = None, n: oInteger = None, offset: oInteger = None, order: oString = None,\
        releaseStatus: oString = None, sort: oString = None, maxUnityVersion: oString = None,\
        minUnityVersion: oString = None, maxAssetVersion: oString = None, minAssetVersion: oString = None,\
        platform: oString = None):

        p = {}

        if user: p["user"] = user
        if featured: p["featured"] = featured
        if tag: p["tag"] = tag
        if userId: p["userId"] = userId
        if n: p["n"] = n
        if offset: p["offset"] = offset
        if order: p["order"] = order
        if releaseStatus: p["releaseStatus"] = releaseStatus
        if sort: p["sort"] = sort
        if maxUnityVersion: p["maxUnityVersion"] = maxUnityVersion
        if minUnityVersion: p["minUnityVersion"] = minUnityVersion
        if maxAssetVersion: p["maxAssetVersion"] = maxAssetVersion
        if minAssetVersion: p["minAssetVersion"] = minAssetVersion
        if platform: p["platform"] = platform

        resp = self.api.call("/avatars", params=p)
        self._raise_for_status(resp)

        avatars = []
        for avatar in resp["data"]:
            avatars.append(objects.Avatar(self, avatar))

        return avatars

    # World calls

    def fetch_world(self, id):
        '''
        Returns World object

            id, str
            WorldID of the world
        '''

        resp = self.api.call("/worlds/"+id)
        self._raise_for_status(resp)

        return objects.World(self, resp["data"])

    def logout(self):
        '''
        Closes client session, invalidates auth cookie
        '''

        resp = self.api.call("/logout", "PUT")
        self._raise_for_status(resp)

        self.api.new_session()
        self.loggedIn = False

    def login(self, username, password):
        '''
        Used to initialize the client for use
        '''

        if self.loggedIn: raise AlreadyLoggedInError("Client is already logged in")

        auth = username+":"+password
        auth = str(base64.b64encode(auth.encode()))[2:-1]

        resp = self.api.call("/auth/user", headers={"Authorization": "Basic "+auth}, no_auth=True)
        self._raise_for_status(resp)

        self.api.set_auth(auth)
        self.me = objects.CurrentUser(self, resp["data"])
        self.loggedIn = True

    def _raise_for_status(self, resp):
        def handle_400():
            if resp["data"]["error"]["message"] == "These users are not friends":
                raise NotFriendsError("These users are not friends")
            elif resp["data"]["error"]["message"] == "\"Users are already friends!\"":
                raise AlreadyFriendsError("Users are already friends!")

        def handle_401():
            raise IncorrectLoginError(resp["data"]["error"]["message"])

        def handle_404():
            msg = ""

            if type(resp["data"]) == bytes:
                try: msg = json.loads(resp["data"].decode())["error"]
                except: msg = str(resp["data"].decode()).split("\"error\":\"")[1].split("\",\"")[0]
            else:
                msg = resp["data"]["error"]["message"]

            raise NotFoundError(msg)

        switch = {
            400: lambda: handle_400(),
            401: lambda: handle_401(),
            404: lambda: handle_404()
        }

        if resp["status"] in switch: switch[resp["status"]]()
        if resp["status"] != 200: raise GeneralError("Unhandled error occured: "+str(resp["data"]))
        if "requiresTwoFactorAuth" in resp["data"]: raise TwoFactorAuthNotSupportedError("2FA is not supported yet.")

    def __init__(self, verify=True):
        self.api = Call(verify)
        self.loggedIn = False
        self.me = None

class AClient(Client):

    # User calls

    async def fetch_me(self):
        '''
        Simply returns newest version of CurrentUser
        '''

        self.cacheFull = False

        resp = await self.api.call("/auth/user")
        self._raise_for_status(resp)

        self.me = aobjects.CurrentUser(self, resp["data"])
        return self.me

    async def fetch_full_friends(self, offline=True, n=0, offset=0):
        '''
        Returns list of User objects
        !! This function uses possibly lot of calls, use with caution

            offline, bool
            Include offline friends or not

            n, int
            Number of friends to return (0 for all)

            offset, int
            Skip first <offset> friends
        '''

        lfriends = await self.fetch_friends(offline, n, offset)
        friends = []

        # Get friends
        for friend in lfriends:
            time.sleep(0)
            friends.append(await friend.fetch_full())

        return friends

    async def fetch_friends(self, offline=False, n=0, offset=0):
        '''
        Returns list of LimitedUser objects

            offline, bool
            Get offline friends instead of online friends

            n, int
            Number of friends to return (0 for all)

            offset, int
            Skip first <offset> friends
        '''

        friends = []

        while True:
            newn = 100
            if not n == 0 and n - len(friends) < 100: newn = n - len(friends)

            last_count = 0

            resp = await self.api.call("/auth/user/friends", params={"offset": offset, "offline": offline, "n": newn})
            self._raise_for_status(resp)

            for friend in resp["data"]:
                last_count += 1
                friends.append(aobjects.LimitedUser(self, friend))

            if last_count < 100:
                break

            offset += 100

        return friends

    async def fetch_user_by_id(self, id):
        '''
        Returns User object

            id, string
            UserId of the user
        '''

        resp = await self.api.call("/users/"+id)
        self._raise_for_status(resp)

        return aobjects.User(self, resp["data"])

    async def fetch_user_by_name(self, name):
        '''
        Returns User object

            name, string
            Name of the user
        '''

        resp = await self.api.call("/users/"+urllib.parse.urlencode(name)+"/name")
        self._raise_for_status(resp)

        return aobjects.User(self, resp["data"])

    # Avatar calls

    async def fetch_avatar(self, id):
        '''
        Returns Avatar object

            id, string,
            AvatarId of the avatar
        '''

        resp = await self.api.call("/avatars/"+id)
        self._raise_for_status(resp)

        return aobjects.Avatar(self, resp["data"])

    async def list_avatars(self, user: oString = None, featured: oBoolean = None, tag: oString = None,\
        userId: oString = None, n: oInteger = None, offset: oInteger = None, order: oString = None,\
        releaseStatus: oString = None, sort: oString = None, maxUnityVersion: oString = None,\
        minUnityVersion: oString = None, maxAssetVersion: oString = None, minAssetVersion: oString = None,\
        platform: oString = None):

        p = {}

        if user: p["user"] = user
        if featured: p["featured"] = featured
        if tag: p["tag"] = tag
        if userId: p["userId"] = userId
        if n: p["n"] = n
        if offset: p["offset"] = offset
        if order: p["order"] = order
        if releaseStatus: p["releaseStatus"] = releaseStatus
        if sort: p["sort"] = sort
        if maxUnityVersion: p["maxUnityVersion"] = maxUnityVersion
        if minUnityVersion: p["minUnityVersion"] = minUnityVersion
        if maxAssetVersion: p["maxAssetVersion"] = maxAssetVersion
        if minAssetVersion: p["minAssetVersion"] = minAssetVersion
        if platform: p["platform"] = platform

        resp = await self.api.call("/avatars", params=p)
        self._raise_for_status(resp)

        avatars = []
        for avatar in resp["data"]:
            avatars.append(aobjects.Avatar(self, avatar))

        return avatars

    # World calls

    async def fetch_world(self, id):
        '''
        Returns World object

            id, str
            WorldID of the world
        '''

        resp = await self.api.call("/worlds/"+id)
        self._raise_for_status(resp)

        return aobjects.World(self, resp["data"])

    async def login(self, username, password):
        '''
        Used to initialize the client for use
        '''

        if self.loggedIn: raise AlreadyLoggedInError("Client is already logged in")

        auth = username+":"+password
        auth = str(base64.b64encode(auth.encode()))[2:-1]

        resp = await self.api.call("/auth/user", headers={"Authorization": "Basic "+auth}, no_auth=True)
        self._raise_for_status(resp)

        self.api.openSession(auth)
        self.me = aobjects.CurrentUser(self, resp["data"])
        self.loggedIn = True

    async def logout(self):
        '''
        Closes client session, invalidates auth cookie
        '''

        resp = await self.api.call("/logout", "PUT")
        self._raise_for_status(resp)

        await self.api.closeSession()
        await asyncio.sleep(0)

        self.api = ACall()
        self.loggedIn = False

    async def wait_for_cache(self):
        while not self.cacheFull:
            await asyncio.sleep(1)

    def __init__(self, verify=True, log_to_console=False):
        super().__init__()

        self.cacheFull = False
        self.log_to_console = log_to_console
        self.api = ACall(verify=verify)
        self.loggedIn = False
        self.me = None
