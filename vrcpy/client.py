from .errors import ClientErrors
from .http import Request

from .currentuser import CurrentUser
from .config import Config

import vrcpy.currentuser

import logging
import asyncio
import base64
import time

def auth_required(method):
    async def _method(self, *args, **kwargs):
        if not self._logged_in:
            raise ClientErrors.NotLoggedIn(
                "Client is not logged in!",
                method
            )

        resp = await method(self, *args, **kwargs)
        return resp
    return _method

class Client:
    def __init__(self, loop=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.me = None
        self.config = None
        self.request = Request(self)

        self._logged_in = False

    @auth_required
    async def fetch_me(self):
        """Fetches new CurrentUser object. This also updates `Client.me`"""

        logging.debug("Fetching me")

        me = await self.request.get("/auth/user")
        me = CurrentUser(
            self,
            self.loop,
            me["data"]
        )

        self.me = me
        return me

    ## System
    async def fetch_config(self) -> Config:
        async with self.request.session.get(
            self.request.base + "/config") as resp:

            assert resp.status == 200
            json = await resp.json()
            self.config = Config(self.loop, json)

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