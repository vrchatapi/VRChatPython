import aiohttp
import logging
import json
from . import __version__

class Request:
    request_retries = 1

    def __init__(self, loop, client, user_agent=None, verify=True):
        self.verify = verify
        self.loop = loop
        self.client = client
        self.user_agent = user_agent or "AIOHTTP/%s (VRCPy/%s)" % aiohttp.__version__, __version__

        self.session = None
        self.base = "https://api.vrchat.cloud/api/1"

    async def _caller(self, method, path, *args, **kwargs):
        if self.client.config is None:
            await self.client.fetch_config()

        if "params" in kwargs:
            for param in kwargs["params"]:
                if type(kwargs["params"][param]) == bool:
                    kwargs["params"][param] = str(kwargs["params"][param]).lower()

            if self.client.config is not None:
                kwargs["params"]["apiKey"] = self.client.config.api_key
        elif self.client.config is not None:
            kwargs["params"] = {"apiKey": self.client.config.api_key}

        async with self.session.request(method, self.base + path, *args, ssl=self.verify, **kwargs) as resp:
            resp = {"status": resp.status, "response": resp, "data": await resp.json()}
            return resp

    async def _call(self, method, path, *args, retries=None, **kwargs):
        if self.session is None:
            self.session = aiohttp.ClientSession(headers={"user-agent": self.user_agent})

        retries = self.request_retries if retries is None else retries
        retries += 1

        resp = None
        for attempt in range(retries):
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