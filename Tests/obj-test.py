import asyncio
import vrcpy

class Avatar(vrcpy.avatar.Avatar):
    def _assign(self, obj):
        pass

class LimitedWorld(vrcpy.world.LimitedWorld):
    def _assign(self, obj):
        pass

class World(vrcpy.world.World):
    def _assign(self, obj):
        pass

class Instance(vrcpy.world.Instance):
    def _assign(self, obj):
        pass

class LimitedUser(vrcpy.user.LimitedUser):
    def _assign(self, obj):
        pass

class User(vrcpy.user.User):
    def _assign(self, obj):
        pass

class CurrentUser(vrcpy.user.CurrentUser):
    def _assign(self, obj):
        pass

client = vrcpy.Client()
loop = asyncio.get_event_loop()

def test(vrc_py, vrc_sdk):
    print(f"Starting tests for {vrc_py.__class__}")

    for attr in vrc_sdk:
        b = False
        for req in vrc_py.required:
            if attr == vrc_py.required[req]["dict_key"]:
                b = True
                break

        for opt in vrc_py.optional:
            if attr == vrc_py.optional[opt]["dict_key"]:
                b = True
                break

        if b:
            continue

        print(f"{vrc_py.__class__} is out of date! Missing attr {attr}")

    for req in vrc_py.required:
        if vrc_py.required[req]["dict_key"] not in vrc_sdk:
            print(f"{vrc_py.__class__} is out of date! Extra required attr {vrc_py.required[req]['dict_key']}")

    print(f"Finished tests for {vrc_py.__class__}")

async def tests():
    a = Avatar(None, None)
    lw = LimitedWorld(None, None)
    w = World(None, None)
    i = Instance(None, None)
    lu = LimitedUser(None, None)
    u = User(None, None)
    cu = CurrentUser(None, None)

    await client.fetch_me()

    a_obj = await client.request.get("/avatar/avtr_0af9d6c9-22be-47b2-a70d-ba83bd5ef547")

    w_obj = await client.request.get("/worlds/wrld_e8c35476-f5f0-45ab-8f4d-c269ff1eda15")
    try:
        _w_obj = await client.fetch_world("wrld_4cf554b4-430c-4f8f-b53e-1f294eed230b")
        i_obj = await client.request.get(f"/worlds/{_w_obj.id}/{_w_obj.instances[0][0]}")
        test(i, i_obj["data"])
    except Exception as e:
        print("World out of date! Can't test Instance. Exception:\n"+str(e))

    lu_obj = await client.request.get("/auth/user/friends", params={
        "offline": "true",
        "n": 1,
        "offset": 0})

    u_obj = await client.request.get("/users/usr_54306e0b-5855-44e2-ac7f-8913a8882a90")
    cu_obj = await client.request.get("/auth/user")

    #test(a, a_obj["data"])
    test(w, w_obj["data"])
    test(lu, lu_obj["data"][0])
    test(u, u_obj["data"])
    test(cu, cu_obj["data"])

async def main():
    await client.login(
        "Username",
        "Password",
        "123456"
    )

    await tests()

    await client.logout()

loop.run_until_complete(main())