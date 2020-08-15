from vrcpy import Client, AClient, objects, aobjects
from vrcpy.errors import WebSocketError, WebSocketOpenedError
import threading
import websocket
import asyncio
import json
import ssl

class _WSSClient:
    def _do_function(self, function, *args):
        if self.clientType == 0:
            function(*args)
        else:
            self.api.loop.create_task(function(*args))

    def _ws_message(self, ws, message):
        message = json.loads(message)

        switch = {
            "friend-location": self._ws_friend_location,
            "friend-online": self._ws_friend_online,
            "friend-active": self._ws_friend_active,
            "friend-offline": self._ws_friend_offline,
            "notification": self._ws_notification
        }

        if message["type"] in switch:
            self._do_function(switch[message["type"]], json.loads(message["content"]))

    def _ws_error(self, ws, error):
        raise WebSocketError(error)

    def _ws_close(self, ws):
        self.ws = None
        self._wssthread = None

    def _ws_open(self, ws):
        pass

    def _open_ws(self):
        if self.ws != None:
            raise WebSocketOpenedError("There is already a websocket open!")

        if asyncio.iscoroutinefunction(self.api.call):
            for cookie in self.api.session.cookie_jar:
                if cookie.key == "auth":
                    auth = cookie.value
        else:
            auth = self.api.session.cookies.get("auth")

        #websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            "wss://pipeline.vrchat.cloud/?authToken="+auth,
            on_message=self._ws_message,
            on_error=self._ws_error,
            on_close=self._ws_close,
            on_open=self._ws_open)

        self._wsthread = threading.Thread(target=self.ws.run_forever)
        self._wsthread.daemon = True
        self._wsthread.start()

class WSSClient(Client, _WSSClient):
    # User WS overwrites

    def on_friend_online(self, friend):
        pass

    def on_friend_active(self, friend):
        pass

    def on_friend_offline(self, friend):
        pass

    def on_friend_location(self, friend, world, location, instance):
        pass

    def on_notification(self, notification):
        pass

    # WS handles

    def _ws_friend_online(self, content):
        self.on_friend_online(objects.User(self, content["user"]))

    def _ws_friend_active(self, content):
        self.on_friend_active(objects.User(self, content["user"]))

    def _ws_friend_location(self, content):
        world = objects.World(self, content["world"])
        user = objects.User(self, content["user"])
        location = objects.Location(self, content["location"])
        instance = objects.Instance(self, content["instance"])

        self.on_friend_location(user, world, location, instance)

    def _ws_friend_offline(self, content):
        self.on_friend_offline(self.fetch_user_by_id(content["userId"]))

    def _ws_notification(self, content):
        self.on_notification(objects.Notification(self, content))

    # Internal Client overwrites

    def login(self, username, password):
        super().login(username, password)
        if self.loggedIn: self._open_ws()

    def login2fa(self, username, password, code=None, verify=False):
        super().login2fa(username, password, code, verify)

    def verify2fa(self, code):
        super().verify2fa(code)
        if self.loggedIn: self._open_ws()

    def logout(self):
        super().logout()
        if not self.loggedIn: self.ws.close()

    def __init__(self, verify=True):
        super().__init__(verify, True) # Caching is always true for ws client

        self.ws = None
        self._wsthread = None
        self.clientType = 0

class AWSSClient(AClient, _WSSClient):
    # User WS overwrites

    async def on_friend_online(self, friend):
        pass

    async def on_friend_active(self, friend):
        pass

    async def on_friend_offline(self, friend):
        pass

    async def on_friend_location(self, friend, world):
        pass

    async def on_notification(self, notification):
        pass

    # WS handles

    async def _ws_friend_online(self, content):
        await self.on_friend_online(aobjects.User(self, content["user"]))

    async def _ws_friend_active(self, content):
        await self.on_friend_active(aobjects.User(self, content["user"]))

    async def _ws_friend_location(self, content):
        world = aobjects.World(self, content["world"])
        user = aobjects.User(self, content["user"])
        location = aobjects.Location(self, content["location"])
        instance = aobjects.Instance(self, content["instance"])

        await self.on_friend_location(user, world, location, instance)

    async def _ws_friend_offline(self, content):
        await self.on_friend_offline(await self.fetch_user_by_id(content["userId"]))

    async def _ws_notification(self, content):
        await self.on_notification(aobjects.Notification(self, content))

    # Internal Client overwrites

    async def login(self, username, password):
        await super().login(username, password)
        if self.loggedIn: self._open_ws()

    async def login2fa(self, username, password, code=None, verify=False):
        await super().login2fa(username, password, code, verify)

    async def verify2fa(self, code):
        await super().verify2fa(code)
        if self.loggedIn: self._open_ws()

    async def logout(self):
        await super().logout()
        if not self.loggedIn: self.ws.close()

    def __init__(self, verify=True):
        super().__init__(verify, True) # Caching is always true for ws client

        self.ws = None
        self._wsthread = None
        self.clientType = 1
