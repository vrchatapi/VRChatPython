# Example of using vrcpy without builtin event loop

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

    # If you want to do your own io eventloop, you'd probably
    #   want to set it up here. We are going to use a very simple one
    #   to get friends in-game every minute

    try:
        while True:
            me = await client.fetch_me()
            for friend in me.online_friends:
                friend = await client.fetch_user(friend)
                print(friend.display_name + " is now in-game!")

            await asyncio.sleep(60)
            print("-" * 25)
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
