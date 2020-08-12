from vrcpy import Client, AClient, objects, aobjects
from vrcpy.errors import WebSocketError, WebSocketOpenedError
import threading
import asyncio
import json

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
            "friend-offline": self.__ws_friend_offline
        }

        if message["type"] in switch:
            self.__do_function(switch[message["type"]], json.loads(message["content"]))

    def __ws_error(self, ws, error):
        raise WebSocketError(error)

    def __ws_close(self, ws):
        self.wss = None
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

        self.ws = websocket.WebSocketApp(
            "wss://pipeline.vrchat.cloud/?authToken="+auth,
            on_message=self.__ws_message,
            on_error=self.__ws_error,
            on_close=self.__ws_close,
            on_open=self.__ws_open)

        self.__wsthread = threading.Thread(target=ws.run_forever)
        self.__wsthread.daemon = True
        self.__wsthread.start()

class WSSClient(__WSSClient, Client):
    # User WS overwrites

    def on_friend_active(self, friend):
        pass

    def on_friend_offline(self, friend):
        pass

    def on_friend_location(self, friend):
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

    # Internal Client overwrites

    def login(self, username, password):
        Client.login(username, password)
        if self.loggedIn: self.__open_ws()

    def login2fa(self, username, password, code=None, verify=False):
        Client.login2fa(username, password, code, verify)
        if self.loggedIn: self.__open_ws()

    def verify2fa(self, code):
        Client.verify2fa(code)
        if self.loggedIn: self.__open_ws()

    def logout(self):
        Client.logout()
        if not self.loggedIn: self.wss.close()

    def __init__(self, verify=True):
        self.ws = None
        self.__wsthread = None
        self.clientType = 0

        Client.__init__(verify, True) # Caching is always true for ws client

class AWSSClient(__WSSClient, AClient):
    # User WS overwrites

    async def on_friend_active(self, friend):
        pass

    async def on_friend_offline(self, friend):
        pass

    async def on_friend_location(self, friend):
        pass

    # WS handles

    async def __ws_friend_active(self, content):
        self.on_friend_active(aobjects.User(content))

    async def __ws_friend_location(self, content):
        #world = content["world"]
        #del content["world"]

        self.on_friend_location(aobjects.User(content))

    async def __ws_friend_offline(self, content):
        self.on_friend_offline(await self.fetch_user_by_id(content["userId"]))

    # Internal Client overwrites

    async def login(self, username, password):
        await AClient.login(username, password)
        if self.loggedIn: self.__open_ws()

    async def login2fa(self, username, password, code=None, verify=False):
        await AClient.login2fa(username, password, code, verify)
        if self.loggedIn: self.__open_ws()

    async def verify2fa(self, code):
        await AClient.verify2fa(code)
        if self.loggedIn: self.__open_ws()

    async def logout(self):
        await AClient.logout()
        if not self.loggedIn: self.wss.close()

    def __init__(self, verify=True):
        self.ws = None
        self.__wsthread = None
        self.clientType = 1

        AClient.__init__(verify, True) # Caching is always true for ws client
