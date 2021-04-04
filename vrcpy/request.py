import json
import asyncio
import aiohttp
import logging
import sys

from vrcpy.errors import RequestErrors, ClientErrors, VRChatErrors

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Request:
    request_retries = 1

    def __init__(self, loop=None, user_agent=None, verify=True, proxy=None):
        self.verify = verify
        # http/s proxy
        self.proxy = ("http://%s/" % proxy) if proxy is not None else None
        self.loop = loop or asyncio.get_event_loop()
        self.user_agent = user_agent or "AIOHTTP/%s (VRCPy)" % aiohttp.__version__

        self.session = None
        self.apiKey = None
        self.base = "https://api.vrchat.cloud/api/1"

    def new_session(self, b64_auth=None):
        if self.session is not None:
            raise RequestErrors.SessionExists("Session already exists")

        # Assume good b64_auth
        headers = {
            "user-agent": self.user_agent
        }

        if b64_auth is not None:
            headers["Authorization"] = "Basic "+b64_auth

        self.session = aiohttp.ClientSession(headers=headers)

    async def close_session(self):
        await self.session.close()
        self.session = None

    async def call(self, path, method="GET", headers={}, params={}, jdict={},
                   no_auth=False, retries=None, verify=None):

        retries = retries or self.request_retries
        verify = verify or self.verify

        resp = None
        for attempt in range(0, retries + 1):
            try:
                resp = await self._call(
                    path, method, headers, params, jdict, no_auth, verify)
                break
            except Exception as e:
                if type(e) in RequestErrors.errors + ClientErrors.errors:
                    raise e.__class__(str(e))

                if attempt == retries:
                    raise RequestErrors.RequestError(
                        "{} ({} retries)".format(e, retries)
                    )

        return resp

    async def _call(self, path, method="GET", headers={}, params={},
                    jdict={}, no_auth=False, verify=None):

        verify = verify or self.verify

        if self.apiKey is None:
            logging.warning("VRC API Key has not been fetched, fetching")

            j = None

            async with aiohttp.ClientSession(headers={
                    "user-agent": self.user_agent}) as session:

                async with session.get(
                        self.base + "/config", proxy=self.proxy) as resp:
                    assert resp.status == 200
                    j = await resp.json()

            try:
                self.apiKey = j["apiKey"]
            except Exception:
                raise ClientErrors.OutOfDate(
                    "This API wrapper is too outdated to function (https://api.vrchat.cloud/api/1/config doesn't contain apiKey)")

        # Conversion to support py bools in request params
        for param in params:
            if isinstance(params[param], bool):
                params[param] = str(params[param]).lower()

        params["apiKey"] = self.apiKey
        if no_auth:
            session = aiohttp.ClientSession(
                headers={"user-agent": self.user_agent})
            resp = await session.request(
                method, self.base + path, params=params, headers=headers,
                json=jdict, ssl=self.verify, proxy=self.proxy)
        else:
            if self.session is None:
                raise RequestErrors.NoSession("No session, not logged in")

            session = None
            resp = await self.session.request(
                method, self.base + path, params=params, headers=headers,
                json=jdict, ssl=self.verify, proxy=self.proxy)

        logging.debug("%s request at %s -> %s" % (method, path, resp.status))

        if resp.status != 200:
            content = await resp.content.read()

            try:
                json = await resp.json()
            except Exception:
                json = None

            Request.raise_for_status(
                {"status": resp.status, "response": resp,
                    "data": json if json is not None else content})

            raise Exception("Something horrible has gone wrong!")

        try:
            response = {
                "status": resp.status, "response": resp, "data": await resp.json()}
        except Exception:
            response = {
                "status": resp.status, "response": resp, "data": await resp.text()}

        # We have to do this since we didn't async with
        await resp.release()
        if session is not None:
            await session.close()

        return response

    @staticmethod
    def raise_for_status(resp):
        if type(resp["data"]) == bytes:
            resp["data"] = json.loads(resp["data"].decode())

        def handle_400():
            if "verified" in resp["data"]:
                raise ClientErrors.MfaInvalid("2FA code is invalid!")

        def handle_401():
            if resp["data"] is None:
                if resp["response"]:
                    raise RequestErrors.Unauthorized(
                        "at %s" % resp["response"].url)

            elif resp["data"]["error"]["message"] == "\"Missing Credentials\"":
                raise ClientErrors.MissingCredentials("Missing Credentials")

        def handle_404():
            pass

        def handle_429():
            raise RequestErrors.RateLimit(resp["data"]["error"]["message"])

        def handle_503():
            raise VRChatErrors.ServiceUnavailable(resp["data"]["error"]["message"])

        switch = {
            400: lambda: handle_400(),
            401: lambda: handle_401(),
            404: lambda: handle_404(),
            429: lambda: handle_429(),
            503: lambda: handle_503()
        }

        if resp["response"].status in switch:
            switch[resp["response"].status]()

        resp["response"].raise_for_status()
