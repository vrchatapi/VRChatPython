from vrcpy.wss import WSSClient
import time

class Client(WSSClient):
    def on_friend_location(self, friend, world, location, instance):
        print("{} is now in {}.".format(friend.displayName,
            "a private world" if location == None else world.name))

    def on_friend_offline(self, friend):
        print("{} went offline.".format(friend.displayName))

    def on_friend_active(self, friend):
        print("{} is now {}.".format(friend.displayName, friend.state))

    def on_friend_online(self, friend):
        print("{} is now online.".format(friend.displayName))

    def on_friend_add(self, friend):
        print("{} is now your friend.".format(friend.displayName))

    def on_friend_delete(self, friend):
        print("{} is no longer your friend.".format(friend.displayName))

    def on_friend_update(self, friend):
        print("{} has updated their profile/account.".format(friend.displayName))

    def on_notification(self, notification):
        print("Got a {} notification from {}.".format(notification.type, notification.senderUsername))

    def on_unhandled_event(self, event, content):
        print("Recieved unhandled event '{}'.".format(event))

    def on_connect(self):
        print("Connected to wss pipeline.")

    def on_disconnect(self):
        print("Disconnected from wss pipeline.")

    def wait_loop(self):
        self.login2fa(input("Username: "), input("Password: "), input("2FA Code: "), True)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logout()

    def __init__(self):
        super().__init__()
        self.wait_loop()

c = Client()
