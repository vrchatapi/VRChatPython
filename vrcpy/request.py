import asyncio
import aiohttp
import requests

from vrcpy.errors import OutOfDateError, NotAuthenticated

class ACall:
    def __init__(self, loop=asyncio.get_event_loop()):
        self.loop = loop
        self.session = None
        self.apiKey = None

    def openSession(self, b64_auth):
        if self.session != None:
            raise AlreadyLoggedInError("A session is already open!")

        # Assume good b64_auth
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
            "Authorization": "Basic "+b64_auth
        }

        self.session = aiohttp.ClientSession(headers)

    async def closeSession(self):
        await self.session.close()
        self.session = None

    async def call(self, path, method="GET", headers={}, params={}, no_auth=False):
        if no_auth:
            resp = await self._call(path, method, headers, params)

        if self.apiKey == None:
            async with self.session.get("https://api.vrchat.cloud/api/1/config") as resp:
                assert resp.status == 200
                j = await resp.json()

            try:
                self.apiKey = j["apiKey"]
            except:
                raise OutOfDateError("This API wrapper is too outdated to function (https://api.vrchat.cloud/api/1/config doesn't contain apiKey)")

        path = "https://api.vrchat.cloud/api/1" + path + "?apiKey=" + self.apiKey
        async with self.session.request(method, path, params=params, headers=headers) as resp:
            if resp.status != 200:
                content = await resp.content.read()

                try: json = await resp.json()
                except: json = None

                return {"status": resp.status, "data": json if not json == None else content}

            json = await resp.json()
            status = resp.status

        return {"status": status, "data": json}

    async def _call(self, path, method="GET", headers={}, params={}):
        h = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
        }

        h.update(headers)

        async with aiohttp.ClientSession(headers=h) as session:
            if self.apiKey == None:
                async with session.get("https://api.vrchat.cloud/api/1/config") as resp:
                    assert resp.status == 200
                    j = await resp.json()

                try:
                    self.apiKey = j["apiKey"]
                except:
                    raise OutOfDateError("This API wrapper is too outdated to function (https://api.vrchat.cloud/api/1/config doesn't contain apiKey)")

            path = "https://api.vrchat.cloud/api/1" + path + "?apiKey=" + self.apiKey
            async with session.request(method, path, params=params, headers=headers) as resp:
                if resp.status != 200:
                    content = await resp.content.read()

                    try: json = await resp.json()
                    except: json = None

                    return {"status": resp.status, "data": json if not json == None else content}

                json = await resp.json()
                status = resp.status

            return {"status": status, "data": json}


class Call:
    def __init__(self):
        self.apiKey = None
        self.b64_auth = None

    def set_auth(self, b64_auth):
        # Assume good b64_auth
        self.b64_auth = b64_auth

    def call(self, path, method="GET", headers={}, params={}, no_auth=False):
        headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"

        if no_auth:
            return self._call(path, method, headers, params)

        if self.b64_auth == None:
            raise NotAuthenticated("Tried to do authenticated request without setting b64 auth (Call.set_auth(b64_auth))!")
        headers["Authorization"] = "Basic "+self.b64_auth

        if self.apiKey == None:
            resp = requests.get("https://api.vrchat.cloud/api/1/config")
            assert resp.status_code == 200

            j = resp.json()
            try:
                self.apiKey = j["apiKey"]
            except:
                raise OutOfDateError("This API wrapper is too outdated to function (https://api.vrchat.cloud/api/1/config doesn't contain apiKey)")

        path = "https://api.vrchat.cloud/api/1" + path + "?apiKey=" + self.apiKey
        resp = requests.request(method, path, headers=headers, params=params)

        if resp.status_code != 200:
            try: json = resp.json()
            except: json = None

            return {"status": resp.status_code, "data": json if not json == None else resp.content}

        return {"status": resp.status_code, "data": resp.json()}

    def _call(self, path, method="GET", headers={}, params={}):
        if self.apiKey == None:
            resp = requests.get("https://api.vrchat.cloud/api/1/config", headers=headers)
            assert resp.status_code == 200

            j = resp.json()
            try:
                self.apiKey = j["apiKey"]
            except:
                raise OutOfDateError("This API wrapper is too outdated to function (https://api.vrchat.cloud/api/1/config doesn't contain apiKey)")

        path = "https://api.vrchat.cloud/api/1" + path + "?apiKey=" + self.apiKey
        resp = requests.request(method, path, headers=headers, params=params)

        if resp.status_code != 200:
            try: json = resp.json()
            except: json = None

            return {"status": resp.status_code, "data": json if not json == None else resp.content}

        return {"status": resp.status_code, "data": resp.json()}
