from .errors import ClientErrors
from .http import Request

from .config import Config

class Client:
    def __init__(self, loop):
        self.loop = loop
        self.me = None
        self.config = None
        self.request = Request()

        self._logged_in = False

    def _auth_required(self, func):
        async def _func(*args, **kwargs):
            if not self._logged_in:
                raise ClientErrors.NotLoggedIn(
                    "Client is not logged in!",
                    func
                )
            await func(*args, **kwargs)

        setattr(self, func.__name__, _func)

    async def fetch_config(self):
        async with self.request.session.get(
            self.request.base + "/config") as resp:

            assert resp.status == 200
            json = await resp.json()
            self.config = Config(self.loop, json)

        return self.config