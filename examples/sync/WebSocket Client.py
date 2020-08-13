from vrcpy.wss import WSSClient
import time

class Client(WSSClient):
    def on_friend_location(self, friend, world, location, instance):
        print("Friend changed world.")

    def on_friend_offline(self, friend):
        print("Friend went offline.")

    def on_friend_active(self, friend):
        print("Friend is now active.")

    def on_notification(self, notification):
        print("Got a notification.")

    def wait_loop(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logout()

    def __init__(self):
        super().__init__()

        self.login2fa(input("Username: "), input("Password: "), input("2FA Code: "), True)
        self.wait_loop()

c = Client()
