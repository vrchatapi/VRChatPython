# Example of logging in

import vrcpy

client = vrcpy.Client()


@client.event
async def on_connect():
    print("WS connected!")


@client.event
async def on_ready():
    print("Cache ready!")


@client.event
async def on_disconnect():
    print("WS disconnected!")

# Blocking, do this last!
client.run(
    username="ExampleName",
    password="ExamplePass",
    mfa="123456"
)
