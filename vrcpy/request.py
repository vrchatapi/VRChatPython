import json
import asyncio
import aiohttp
import logging

from vrcpy.errors import RequestErrors, ClientErrors, VRChatErrors


class Request:
    request_retries = 1

    def __init__(self, loop=None, user_agent=None, verify=True):
        self.verify = verify
        self.loop = loop or asyncio.get_event_loop()
        self.user_agent = user_agent or "AIOHTTP/%s (VRCPy)" % aiohttp.__version__

        self.session = None
        self.api_key = None
        self.base = "https://api.vrchat.cloud/api/1"

    async def _caller(self, method, path, *args, **kwargs):
        if self.api_key is None:
            async with self.session.get(self.base + "/config") as resp:
                assert resp.status == 200

                j = await resp.json()
                self.api_key = j["apiKey"]

        if "params" in kwargs:
            for param in kwargs["params"]:
                if type(kwargs["params"][param]) == bool:
                    kwargs["params"][param] = str(kwargs["params"][param]).lower()

            kwargs["params"]["apiKey"] = self.api_key
        else:
            kwargs["params"] = {"apiKey": self.api_key}

        async with self.session.request(method, self.base + path, *args, ssl=self.verify, **kwargs) as resp:
            resp = {"status": resp.status, "response": resp, "data": await resp.json()}
            return resp

    async def _call(self, method, path, *args, **kwargs):
        if self.session is None:
            self.session = aiohttp.ClientSession(headers={"user-agent": self.user_agent})

        resp = None
        for attempt in range(self.request_retries + 1):
            try:
                resp = await self._caller(method, path, *args, **kwargs)
                break
            except Exception as e:
                if type(e) in RequestErrors.errors + ClientErrors.errors:
                    raise e.__class__(str(e))

                if attempt == self.request_retries:
                    raise RequestErrors.RequestError(
                        "{} ({} retries)".format(e, self.request_retries)
                    )

        self.raise_for_errors(resp)
        return resp

    async def close_session(self):
        await self.session.close()

    async def get(self, path, *args, **kwargs):
        resp = await self._call("GET", path, *args, **kwargs)
        return resp

    async def post(self, path, *args, **kwargs):
        resp = await self._call("POST", path, *args, **kwargs)
        return resp

    async def put(self, path, *args, **kwargs):
        resp = await self._call("PUT", path, *args, **kwargs)
        return resp

    async def delete(self, path, *args, **kwargs):
        resp = await self._call("DELETE", path, *args, **kwargs)
        return resp

    async def patch(self, path, *args, **kwargs):
        resp = await self._call("PATCH", path, *args, **kwargs)
        return resp

    def raise_for_errors(self, resp):
        def on_200():
            if "requiresTwoFactorAuth" in resp["data"]:
                raise ClientErrors.MfaRequired("Account login requires mfa")

        def on_429():
            raise RequestErrors.RateLimit("You are being rate limited")

        switch = {
            200: on_200,
            429: on_429
        }

        if resp["status"] in switch:
            switch[resp["status"]]()