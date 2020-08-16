from vrcpy.wss import AWSSClient
import asyncio
import time

class AClient(AWSSClient):
    async def on_friend_location(self, friend, world, location, instance):
        print("{} is now in {}.".format(friend.displayName,
            "a private world" if location == None else world.name))

    async def on_friend_offline(self, friend):
        print("{} went offline.".format(friend.displayName))

    async def on_friend_active(self, friend):
        print("{} is now {}.".format(friend.displayName, friend.state))

    async def on_friend_online(self, friend):
        print("{} is now online.".format(friend.displayName))

    async def on_friend_add(self, friend):
        print("{} is now your friend.".format(friend.displayName))

    async def on_friend_delete(self, friend):
        print("{} is no longer your friend.".format(friend.displayName))

    async def on_friend_update(self, friend):
        print("{} has updated their profile/account.".format(friend.displayName))

    async def on_notification(self, notification):
        print("Got a {} notification from {}.".format(notification.type, notification.senderUsername))

    async def on_unhandled_event(self, event, content):
        print("Recieved unhandled event '{}'.".format(event))

    async def on_connect(self):
        print("Connected to wss pipeline.")

    async def on_disconnect(self):
        print("Disconnected from wss pipeline.")

    async def wait_loop(self):
        await self.login2fa(input("Username: "), input("Password: "), input("2FA Code: "), True)

        while True:
            await asyncio.sleep(1)

    def __init__(self):
        super().__init__()
        try:
            asyncio.get_event_loop().run_until_complete(self.wait_loop())
        except KeyboardInterrupt:
            asyncio.get_event_loop().run_until_complete(self.logout())

c = AClient()
