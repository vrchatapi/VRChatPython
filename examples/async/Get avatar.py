import asyncio
import vrcpy

async def main():
    # Initialise vrcpy wrapper client and login with username + password
    client = vrcpy.AClient()
    await client.login("username", "password")

    # Get avatar via id
    a = await client.fetch_avatar("avtr_fa5303c6-78d1-451c-a678-faf3eadb5c50")
    author = await a.author() # Get author of the avatar
    print("Avatar '"+a.name+"' was made by "+author.displayName)
    ## This should print "Avatar 'Etoigne' was made by Katfish"

    # Close client session cleanly, invalidate auth cookie
    await client.logout()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
