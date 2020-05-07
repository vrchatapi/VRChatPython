from vrcpy.objects import *
import vrcpy.types

## Avatar

class Avatar(Avatar):
    async def author(self):
        resp = await self.client.api.call("/users/"+self.authorId)
        self.client._raise_for_status(resp)
        return User(self.client, resp["data"])

## User

class CurrentUser(CurrentUser):
    obj = "CurrentUser"

    async def avatars(self, releaseStatus=types.ReleaseStatus.All):
        '''
        Returns array of Avatar objects owned by the current user

            releaseStatus, string
            One of types type.ReleaseStatus
        '''

        resp = await self.client.api.call("/avatars",
            params={"releaseStatus": releaseStatus, "user": "me"})
        self.client._raise_for_status(resp)

        avatars = []
        for avatar in resp["data"]:
            if avatar["authorId"] == self.id:
                avatars.append(Avatar(self.client, avatar))

        return avatars

    def __init__(self, client, obj):
        super().__init__(client, obj)

## World

class LimitedWorld(LimitedWorld):
    async def author(self):
        resp = await self.client.api.call("/users/"+self.authorId)
        self.client._raise_for_status(resp)
        return User(self.client, resp["data"])

class Instance(Instance):
    async def world(self):
        resp = await self.client.api.call("/worlds/"+self.worldId)
        self.client._raise_for_status(resp)
        return World(resp["data"])
