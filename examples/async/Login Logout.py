import asyncio
import vrcpy

# Normal vanilla login
async def main():
    # Initialise vrcpy wrapper client and login with username + password
    client = vrcpy.AClient()
    await client.login("username", "password")

    # Close client session, invalidate auth cookie
    await client.logout()

# 2-Factor-Auth account login
def twofactorauth():
    # Initialise vrcpy wrapper client
    client = vrcpy.AClient()

    # Login with username + password, then verify 2-factor-auth code
    # Can be done in 1 line via:
    #   await client.login2fa("username", "password", code="123456", verify=True)
    await client.login2fa("username", "password")
    await client.verify2fa("123456")

    # Close client session, invalidate auth cookie
    await client.logout()

def run_main():
    asyncio.get_event_loop().run_until_complete(main())

def run_2fa():
    asyncio.get_event_loop().run_until_complete(twofactorauth())
