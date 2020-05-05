import asyncio
import aiohttp

class aCall:
    def __init__(self, loop=asyncio.get_event_loop()):
        self.loop = loop
        self.session = None
        self.apiKey = None

    def openSession(self, b64_auth):
        if self.session != None:
            raise Exception("A session is already open!")

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
                raise Exception("This API wrapper is too outdated to function (https://api.vrchat.cloud/api/1/config doesn't contain apiKey)")

        path = "https://api.vrchat.cloud/api/1" + path + "?apiKey=" + self.apiKey
        async with self.session.request(method, path, params=params, headers=headers) as resp:
            if resp.status != 200:
                content = await resp.content.read()

                try: json = await resp.json()
                except: json = None

                return {"status": resp.status, "data": json if json not None else content}

            json = await resp.json()
            status = resp.status

        return {"status": status, "data": json}

    async def _call(self, path, method="GET", headers={}, params={}):
        async with aiohttp.ClientSession(headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"}) as session:
            if self.apiKey == None:
                async with session.get("https://api.vrchat.cloud/api/1/config") as resp:
                    assert resp.status == 200
                    j = await resp.json()

                try:
                    self.apiKey = j["apiKey"]
                except:
                    raise Exception("This API wrapper is too outdated to function (https://api.vrchat.cloud/api/1/config doesn't contain apiKey)")

            path = "https://api.vrchat.cloud/api/1" + path + "?apiKey=" + self.apiKey
            async with session.request(method, path, params=params, headers=headers) as resp:
                if resp.status != 200:
                    content = await resp.content.read()

                    try: json = await resp.json()
                    except: json = None

                    return {"status": resp.status, "data": json if json not None else content}

                json = await resp.json()
                status = resp.status

            return {"status": status, "data": json}
