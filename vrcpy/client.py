from vrcpy.request import *
from vrcpy.errors import *
from vrcpy import objects
from vrcpy import aobjects
import base64

class Client:
    def __init__(self):
        self.api = Call()
        self.loggedIn = False
        self.me = None

    def login(self, username, password):
        if self.loggedIn: raise AlreadyLoggedInError("Client is already logged in")

        auth = username+":"+password
        auth = str(base64.b64encode(auth.encode()))[2:-1]

        resp = self.api.call("/auth/user", headers={"Authorization": "Basic "+auth}, no_auth=True)
        if resp["status"] == 401: raise IncorrectLoginError(resp["data"]["error"]["message"])
        if "requiresTwoFactorAuth" in resp["data"]: raise TwoFactorAuthNotSupportedError("2FA is not supported yet.")
        if resp["status"] != 200: raise GeneralError("Unhandled error occured: "+resp["data"])

        self.api.set_auth(auth)
        self.me = objects.CurrentUser(resp["data"])
        self.loggedIn = True

    def logout(self):
        self.api = Call()
        self.loggedIn = False

class AClient:
    def __init__(self):
        self.api = ACall()
        self.loggedIn = False
        self.me = None

    async def login(self, username, password):
        if self.loggedIn: raise AlreadyLoggedInError("Client is already logged in")

        auth = username+":"+password
        auth = str(base64.b64encode(auth.encode()))[2:-1]

        resp = await self.api.call("/auth/user", headers={"Authorization": "Basic "+auth}, no_auth=True)
        if resp["status"] == 401: raise IncorrectLoginError(resp["data"]["error"]["message"])
        if "requiresTwoFactorAuth" in resp["data"]: raise TwoFactorAuthNotSupportedError("2FA is not supported yet.")
        if resp["status"] != 200: raise GeneralError("Unhandled error occured: "+resp["data"])

        self.api.openSession(auth)
        self.me = objects.CurrentUser(resp["data"])
        self.loggedIn = True

    async def logout(self):
        await self.api.closeSession()
        await asyncio.sleep(0)

        self.api = ACall()
        self.loggedIn = False
