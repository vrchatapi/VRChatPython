from vrcpy.request import *
from vrcpy.errors import *
from vrcpy import objects
from vrcpy import aobjects
import base64

class Client:
    def fetch_me(self):
        '''
            Simply returns newest version of CurrentUser
        '''

        resp = self.api.call("/auth/user")
        self._raise_for_status(resp)

        self.me = objects.CurrentUser(self, resp["data"])
        return self.me

    def fetch_avatar(self, id):
        '''
            ID is the AvatarId of the avatar
            Returns Avatar object
        '''

        resp = self.api.call("/avatars/"+id)
        self._raise_for_status(resp)

        return objects.Avatar(self, resp["data"])

    def fetch_user_by_id(self, id):
        '''
        Returns User or FriendUser
            id, string The users id
        '''

        resp = self.api.call("/users/"+id)
        self._raise_for_status(resp)

        return objects.User(self, resp["data"])

    def logout(self):
        self.api = Call()
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
        if "requiresTwoFactorAuth" in resp["data"]: raise TwoFactorAuthNotSupportedError("2FA is not supported yet.")
        if resp["status"] == 404: raise NotFoundError(resp["data"]["error"]["message"])
        if resp["status"] != 200: raise GeneralError("Unhandled error occured: "+str(resp["data"]))

    def __init__(self):
        self.api = Call()
        self.loggedIn = False
        self.me = None

class AClient(Client):
    async def fetch_me(self):
        '''
            Simply returns newest version of CurrentUser
        '''
        resp = await self.api.call("/auth/user")
        self._raise_for_status(resp)

        self.me = aobjects.CurrentUser(self, resp["data"])
        return self.me

    async def fetch_avatar(self, id):
        '''
            ID is the AvatarId of the avatar
            Returns Avatar object
        '''

        resp = await self.api.call("/avatars/"+id)
        self._raise_for_status(resp)

        return aobjects.Avatar(self, resp["data"])

    async def fetch_user_by_id(self, id):
        '''
        Returns User or FriendUser
            id, string The users id
        '''

        resp = await self.api.call("/users/"+id)
        self._raise_for_status(resp)

        return objects.User(self, resp["data"])

    async def login(self, username, password):
        '''
            Used to initialize the client for use
        '''
        if self.loggedIn: raise AlreadyLoggedInError("Client is already logged in")

        auth = username+":"+password
        auth = str(base64.b64encode(auth.encode()))[2:-1]

        resp = await self.api.call("/auth/user", headers={"Authorization": "Basic "+auth}, no_auth=True)
        if resp["status"] == 401: raise IncorrectLoginError(resp["data"]["error"]["message"])
        if "requiresTwoFactorAuth" in resp["data"]: raise TwoFactorAuthNotSupportedError("2FA is not supported yet.")
        if resp["status"] != 200: raise GeneralError("Unhandled error occured: "+resp["data"])

        self.api.openSession(auth)
        self.me = aobjects.CurrentUser(self, resp["data"])
        self.loggedIn = True

    async def logout(self):
        await self.api.closeSession()
        await asyncio.sleep(0)

        self.api = ACall()
        self.loggedIn = False

    def __init__(self):
        super().__init__()

        self.api = ACall()
        self.loggedIn = False
        self.me = None
