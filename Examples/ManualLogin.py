# Example of logging in with more control over async loop creation

import vrcpy
import asyncio

loop = asyncio.get_event_loop()
client = vrcpy.Client(loop=loop)


async def main():
    await client.login(
        username="ExampleName",
        password="ExamplePass",
        mfa="123456"
    )

    try:
        # Start the ws event loop
        await client.start()
    except KeyboardInterrupt:
        await client.logout()


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
loop.run_until_complete(main())
