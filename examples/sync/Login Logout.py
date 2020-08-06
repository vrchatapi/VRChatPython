import vrcpy

# Normal vanilla login
def main():
    # Initialise vrcpy wrapper client and login with username + password
    client = vrcpy.Client()
    client.login("username", "password")

    # Close client session, invalidate auth cookie
    client.logout()

# 2-Factor-Auth account login
def twofactorauth():
    # Initialise vrcpy wrapper client
    client = vrcpy.Client()

    # Login with username + password, then verify 2-factor-auth code
    # Can be done in 1 line via:
    #   client.login2fa("username", "password", code="123456", verify=True)
    client.login2fa("username", "password")
    client.verify2fa("123456")

    # Close client session, invalidate auth cookie
    client.logout()
