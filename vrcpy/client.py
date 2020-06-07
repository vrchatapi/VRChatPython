from vrcpy._hardtyping import *
from vrcpy.request import *
from vrcpy.errors import *
from vrcpy import objects
from vrcpy import aobjects
import base64
import time
import json

class Client:
    # User calls

    def fetch_me(self) -> CurrentUser:
        '''
        Simply returns newest version of CurrentUser
        '''

        resp = self.api.call("/auth/user")
        self._raise_for_status(resp)

        self.me = objects.CurrentUser(self, resp["data"])
        return self.me

    def fetch_full_friends(self) -> UserList:
        '''
        Returns list of User objects
        !! This function uses possibly lot of calls, use with caution
        '''

        self.fetch_me()
        friends = []

        # Get friends
        for friend in self.me.friends:
            time.sleep(0)
            resp = self.api.call("/users/"+friend)
            try:
                self._raise_for_status(resp)
            except NotFoundError:
                # User no longer exists
                continue

            friends.append(objects.User(self, resp))

        return friends

    def fetch_friends(self) -> UserList:
        '''
        Returns list of LimitedUser objects
        '''

        self.fetch_me()
        friends = []

        # Get all pages of friends if > 100
        for offset in range(0, len(self.me.friends), 100):
            resp = self.api.call("/auth/user/friends", json={"offset": offset, "offline": True})
            self._raise_for_status(resp)

            for friend in resp["data"]:
                friends.append(objects.LimitedUser(self, friend))

        for offset in range(0, len(self.me.friends), 100):
            resp = self.api.call("/auth/user/friends", json={"offset": offset, "offline": False})
            self._raise_for_status(resp)

            for friend in resp["data"]:
                friends.append(objects.LimitedUser(self, friend))

        return friends

    def fetch_user_by_id(self, id) -> User:
        '''
        Returns User or FriendUser object

            id, string
            UserId of the user
        '''

        resp = self.api.call("/users/"+id)
        self._raise_for_status(resp)

        return objects.User(self, resp["data"])

    def fetch_avatar(self, id) -> Avatar:
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
        platform: oString = None) -> AvatarList:

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
            avatars.append(objects.Avatar(client, avatar))

        return avatars

    def logout(self):
        '''
        Closes client session
        '''

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
        if resp["status"] == 401: raise IncorrectLoginError(resp["data"]["error"]["message"])
        if resp["status"] == 404:
            if type(resp["data"]) == bytes:
                try: raise NotFoundError(json.loads(resp["data"].decode()))
                except: raise NotFoundError(str(resp["data"].decode()))
            raise NotFoundError(resp["data"]["error"]["message"])
        if resp["status"] != 200: raise GeneralError("Unhandled error occured: "+str(resp["data"]))
        if "requiresTwoFactorAuth" in resp["data"]: raise TwoFactorAuthNotSupportedError("2FA is not supported yet.")

    def __init__(self):
        self.api = Call()
        self.loggedIn = False
        self.me = None

class AClient(Client):
    async def fetch_me(self) -> CurrentUser:
        '''
        Simply returns newest version of CurrentUser
        '''

        resp = await self.api.call("/auth/user")
        self._raise_for_status(resp)

        self.me = aobjects.CurrentUser(self, resp["data"])
        return self.me

    async def fetch_full_friends(self) -> UserList:
        '''
        Returns list of User objects
        !! This function uses possibly lot of calls, use with caution
        '''

        await self.fetch_me()
        friends = []

        # Get friends
        for friend in self.me.friends:
            await asyncio.sleep(0)
            resp = await self.api.call("/users/"+friend)
            try:
                self._raise_for_status(resp)
            except NotFoundError:
                # User no longer exists
                continue

            friends.append(aobjects.User(self, resp))

        return friends

    async def fetch_friends(self) -> UserList:
        '''
        Returns list of LimitedUser objects
        '''

        await self.fetch_me()
        friends = []

        # Get all pages of friends if > 100
        for offset in range(0, len(self.me.friends), 100):
            resp = await self.api.call("/auth/user/friends", json={"offset": offset, "offline": True})
            self._raise_for_status(resp)

            for friend in resp["data"]:
                friends.append(aobjects.LimitedUser(self, friend))

        for offset in range(0, len(self.me.friends), 100):
            resp = await self.api.call("/auth/user/friends", json={"offset": offset, "offline": False})
            self._raise_for_status(resp)

            for friend in resp["data"]:
                friends.append(aobjects.LimitedUser(self, friend))

        return friends

    async def fetch_user_by_id(self, id) -> User:
        '''
        Returns User or FriendUser object

            id, string
            UserId of the user
        '''

        resp = await self.api.call("/users/"+id)
        self._raise_for_status(resp)

        return objects.User(self, resp["data"])

    async def fetch_avatar(self, id) -> Avatar:
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
        platform: oString = None) -> AvatarList:

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
        Closes client session
        '''

        await self.api.closeSession()
        await asyncio.sleep(0)

        self.api = ACall()
        self.loggedIn = False

    def __init__(self):
        super().__init__()

        self.api = ACall()
        self.loggedIn = False
        self.me = None
