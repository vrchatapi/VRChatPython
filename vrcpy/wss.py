from vrcpy import Client, AClient, objects, aobjects
from vrcpy.errors import WebSocketError, WebSocketOpenedError
import threading
import websocket
import asyncio
import json
import ssl

class __WSSClient:
    def __do_function(self, function, *args):
        if self.clientType == 0:
            function(*args)
        else:
            self.api.loop.create_task(function(*args))

    def __ws_message(self, ws, message):
        message = json.loads(message)

        switch = {
            "friend-location": self.__ws_friend_location,
            "friend-active": self.__ws_friend_active,
            "friend-offline": self.__ws_friend_offline,
            "notification": self.__ws_notification
        }

        if message["type"] in switch:
            self.__do_function(switch[message["type"]], json.loads(message["content"]))

    def __ws_error(self, ws, error):
        raise WebSocketError(error)

    def __ws_close(self, ws):
        self.ws = None
        self.__wssthread = None

    def __ws_open(self, ws):
        pass

    def __open_ws(self):
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
            on_message=self.__ws_message,
            on_error=self.__ws_error,
            on_close=self.__ws_close,
            on_open=self.__ws_open)

        self.__wsthread = threading.Thread(target=self.ws.run_forever)
        self.__wsthread.daemon = True
        self.__wsthread.start()

class WSSClient(Client, __WSSClient):
    # User WS overwrites

    def on_friend_active(self, friend):
        pass

    def on_friend_offline(self, friend):
        pass

    def on_friend_location(self, friend):
        pass

    def on_notification(self, notification):
        pass

    # WS handles

    def __ws_friend_active(self, content):
        self.on_friend_active(objects.User(content))

    def __ws_friend_location(self, content):
        #world = content["world"]
        #del content["world"]

        self.on_friend_location(objects.User(content))

    def __ws_friend_offline(self, content):
        self.on_friend_offline(self.fetch_user_by_id(content["userId"]))

    def __ws_notification(self, content):
        self.on_notification(None)

    # Internal Client overwrites

    def login(self, username, password):
        super().login(username, password)
        if self.loggedIn: self.__open_ws()

    def login2fa(self, username, password, code=None, verify=False):
        super().login2fa(username, password, code, verify)

    def verify2fa(self, code):
        super().verify2fa(code)
        if self.loggedIn: self.__open_ws()

    def logout(self):
        super().logout()
        if not self.loggedIn: self.ws.close()

    def __init__(self, verify=True):
        super().__init__(verify, True) # Caching is always true for ws client

        self.ws = None
        self.__wsthread = None
        self.clientType = 0

class AWSSClient(AClient, __WSSClient):
    # User WS overwrites

    async def on_friend_active(self, friend):
        pass

    async def on_friend_offline(self, friend):
        pass

    async def on_friend_location(self, friend):
        pass

    async def on_notification(self, notification):
        pass

    # WS handles

    async def __ws_friend_active(self, content):
        await self.on_friend_active(aobjects.User(content))

    async def __ws_friend_location(self, content):
        #world = content["world"]
        #del content["world"]

        await self.on_friend_location(aobjects.User(content))

    async def __ws_friend_offline(self, content):
        await self.on_friend_offline(await self.fetch_user_by_id(content["userId"]))

    async def __ws_notification(self, content):
        await self.on_notification(None)

    # Internal Client overwrites

    async def login(self, username, password):
        await super().login(username, password)
        if self.loggedIn: self.__open_ws()

    async def login2fa(self, username, password, code=None, verify=False):
        await super().login2fa(username, password, code, verify)

    async def verify2fa(self, code):
        await super().verify2fa(code)
        if self.loggedIn: self.__open_ws()

    async def logout(self):
        await super().logout()
        if not self.loggedIn: self.ws.close()

    def __init__(self, verify=True):
        super().__init__(verify, True) # Caching is always true for ws client

        self.ws = None
        self.__wsthread = None
        self.clientType = 1
