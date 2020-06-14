from vrcpy._hardtyping import *
from vrcpy.request import *
from vrcpy.errors import AlreadyLoggedInError
from vrcpy import objects
from vrcpy import aobjects

from datetime import datetime

import urllib
import base64
import time
import json

class Client:
    '''
    Main client interface for VRC

        verify, boolean
        If should verify ssl certificates on requests
    '''

    # Log

    def _log(self, log): # TODO: Finish logging, also, dunno how I'm gonna do this yet
        dt = datetime.now().strftime("%d/%m - %H:%M:%S")

        if self.log_to_console:
            print("[%s] %s" % dt, log)

    # User calls

    def fetch_me(self):
        '''
        Used to refresh client.me
        Returns CurrentUser object
        '''

        resp = self.api.call("/auth/user")

        self.me = objects.CurrentUser(self, resp["data"])
        return self.me

    def fetch_full_friends(self, offline=True, n=0, offset=0):
        '''
        Used to get friends of current user
        !! This function uses possibly lot of calls, use with caution

            offline, boolean
            Include offline friends or not

            n, integer
            Number of friends to return (0 for all)

            offset, integer
            Skip first <offset> friends

        Returns list of User objects
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
        Used to get friends of current user

            offline, boolean
            Get offline friends instead of online friends

            n, integer
            Number of friends to return (0 for all)

            offset, integer
            Skip first <offset> friends

        Returns list of LimitedUser objects
        '''

        friends = []

        while True:
            newn = 100
            if not n == 0 and n - len(friends) < 100: newn = n - len(friends)

            last_count = 0

            resp = self.api.call("/auth/user/friends", params={"offset": offset, "offline": offline, "n": newn})

            for friend in resp["data"]:
                last_count += 1
                friends.append(objects.LimitedUser(self, friend))

            if last_count < 100:
                break

            offset += 100

        return friends

    def fetch_user_by_id(self, id):
        '''
        Used to get a user via id

            id, string
            UserId of the user

        Returns User object
        '''

        resp = self.api.call("/users/"+id)
        return objects.User(self, resp["data"])

    def fetch_user_by_name(self, name):
        '''
        Used to get a user via id

            name, string
            Name of the user

        Returns User object
        '''

        resp = self.api.call("/users/"+urllib.parse.urlencode(name)+"/name")
        return objects.User(self, resp["data"])

    # Avatar calls

    def fetch_avatar(self, id):
        '''
        Used to get avatar via id

            id, string
            AvatarId of the avatar

        Returns Avatar object
        '''

        resp = self.api.call("/avatars/"+id)
        return objects.Avatar(self, resp["data"])

    def list_avatars(self, user: oString = None, featured: oBoolean = None, tag: oString = None,\
        userId: oString = None, n: oInteger = None, offset: oInteger = None, order: oString = None,\
        releaseStatus: oString = None, sort: oString = None, maxUnityVersion: oString = None,\
        minUnityVersion: oString = None, maxAssetVersion: oString = None, minAssetVersion: oString = None,\
        platform: oString = None):

        '''
        Used to get list of avatars

            user, string
            Type of user (me, friends)

            featured, boolean
            If the avatars are featured

            tag, string list
            List of tags the avatars have

            userId, string
            ID of the user that made the avatars

            n, integer
            Number of avatars to return

            offset, integer
            Skip first <offset> avatars

            order, string
            Sort <sort> by "descending" or "ascending" order

            releaseStatus, string
            ReleaseStatus of avatars

            sort, string
            Sort by "created", "updated", "order", "_created_at", "_updated_at"

            maxUnityVersion, string
            Max version of unity the avatars were uploaded from

            minUnityVersion, string
            Min version of unity the avatars were uploaded from

            maxAssetVersion, string
            Max of 'asset version' of the avatars

            minAssetVersion, string
            Min of 'asset version' of the avatars

            platform, string
            Unity platform avatars were uploaded from

        Returns list of Avatar objects
        '''

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

        avatars = []
        for avatar in resp["data"]:
            avatars.append(objects.Avatar(self, avatar))

        return avatars

    # World calls

    def fetch_world(self, id):
        '''
        Used to get world via id

            id, string
            ID of the world

        Returns World object
        '''

        resp = self.api.call("/worlds/"+id)
        return objects.World(self, resp["data"])

    def logout(self):
        '''
        Closes client session, invalidates auth cookie
        Returns void
        '''

        resp = self.api.call("/logout", "PUT")

        self.api.new_session()
        self.loggedIn = False

    def login(self, username, password):
        '''
        Used to initialize the client for use

            username, string
            Username of VRC account

            password, string
            Password of VRC account

        Returns void
        '''

        if self.loggedIn: raise AlreadyLoggedInError("Client is already logged in")

        auth = username+":"+password
        auth = str(base64.b64encode(auth.encode()))[2:-1]

        resp = self.api.call("/auth/user", headers={"Authorization": "Basic "+auth}, no_auth=True)

        self.api.set_auth(auth)
        self.me = objects.CurrentUser(self, resp["data"])
        self.loggedIn = True

    def __init__(self, verify=True):
        self.api = Call(verify)
        self.loggedIn = False
        self.me = None

class AClient(Client):
    '''
    Main client interface for VRC

        verify, boolean
        If should verify ssl certificates on requests
    '''

    # User calls

    async def fetch_me(self):
        '''
        Used to refresh client.me
        Returns CurrentUser object
        '''

        self.cacheFull = False
        resp = await self.api.call("/auth/user")

        self.me = aobjects.CurrentUser(self, resp["data"])
        return self.me

    async def fetch_full_friends(self, offline=True, n=0, offset=0):
        '''
        Used to get friends of current user
        !! This function uses possibly lot of calls, use with caution

            offline, boolean
            Include offline friends or not

            n, integer
            Number of friends to return (0 for all)

            offset, integer
            Skip first <offset> friends

        Returns list of User objects
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
        Used to get friends of current user

            offline, boolean
            Get offline friends instead of online friends

            n, integer
            Number of friends to return (0 for all)

            offset, integer
            Skip first <offset> friends

        Returns list of LimitedUser objects
        '''

        friends = []

        while True:
            newn = 100
            if not n == 0 and n - len(friends) < 100: newn = n - len(friends)

            last_count = 0

            resp = await self.api.call("/auth/user/friends", params={"offset": offset, "offline": offline, "n": newn})

            for friend in resp["data"]:
                last_count += 1
                friends.append(aobjects.LimitedUser(self, friend))

            if last_count < 100:
                break

            offset += 100

        return friends

    async def fetch_user_by_id(self, id):
        '''
        Used to get a user via id

            id, string
            UserId of the user

        Returns User object
        '''

        resp = await self.api.call("/users/"+id)
        return aobjects.User(self, resp["data"])

    async def fetch_user_by_name(self, name):
        '''
        Used to get a user via id

            name, string
            Name of the user

        Returns User object
        '''

        resp = await self.api.call("/users/"+urllib.parse.urlencode(name)+"/name")
        return aobjects.User(self, resp["data"])

    # Avatar calls

    async def fetch_avatar(self, id):
        '''
        Used to get avatar via id

            id, string
            AvatarId of the avatar

        Returns Avatar object
        '''

        resp = await self.api.call("/avatars/"+id)
        return aobjects.Avatar(self, resp["data"])

    async def list_avatars(self, user: oString = None, featured: oBoolean = None, tag: oString = None,\
        userId: oString = None, n: oInteger = None, offset: oInteger = None, order: oString = None,\
        releaseStatus: oString = None, sort: oString = None, maxUnityVersion: oString = None,\
        minUnityVersion: oString = None, maxAssetVersion: oString = None, minAssetVersion: oString = None,\
        platform: oString = None):

        '''
        Used to get list of avatars

            user, string
            Type of user (me, friends)

            featured, boolean
            If the avatars are featured

            tag, string list
            List of tags the avatars have

            userId, string
            ID of the user that made the avatars

            n, integer
            Number of avatars to return

            offset, integer
            Skip first <offset> avatars

            order, string
            Sort <sort> by "descending" or "ascending" order

            releaseStatus, string
            ReleaseStatus of avatars

            sort, string
            Sort by "created", "updated", "order", "_created_at", "_updated_at"

            maxUnityVersion, string
            Max version of unity the avatars were uploaded from

            minUnityVersion, string
            Min version of unity the avatars were uploaded from

            maxAssetVersion, string
            Max of 'asset version' of the avatars

            minAssetVersion, string
            Min of 'asset version' of the avatars

            platform, string
            Unity platform avatars were uploaded from

        Returns list of Avatar objects
        '''

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

        avatars = []
        for avatar in resp["data"]:
            avatars.append(aobjects.Avatar(self, avatar))

        return avatars

    # World calls

    async def fetch_world(self, id):
        '''
        Used to get world via id

            id, string
            ID of the world

        Returns World object
        '''

        resp = await self.api.call("/worlds/"+id)
        return aobjects.World(self, resp["data"])

    async def logout(self):
        '''
        Closes client session, invalidates auth cookie
        Returns void
        '''

        resp = await self.api.call("/logout", "PUT")

        await self.api.closeSession()
        await asyncio.sleep(0)

        self.api = ACall()
        self.loggedIn = False

    async def login(self, username, password):
        '''
        Used to initialize the client for use

            username, string
            Username of VRC account

            password, string
            Password of VRC account

        Returns void
        '''

        if self.loggedIn: raise AlreadyLoggedInError("Client is already logged in")

        auth = username+":"+password
        auth = str(base64.b64encode(auth.encode()))[2:-1]

        resp = await self.api.call("/auth/user", headers={"Authorization": "Basic "+auth}, no_auth=True)

        self.api.openSession(auth)
        self.me = aobjects.CurrentUser(self, resp["data"])
        self.loggedIn = True

    async def wait_for_cache(self):
        '''
        Used to stall task and wait for caching to finish
        Returns void
        '''

        while not self.cacheFull:
            await asyncio.sleep(1)

    def __init__(self, verify=True):
        super().__init__()

        self.cacheFull = False
        self.api = ACall(verify=verify)
        self.loggedIn = False
        self.me = None
