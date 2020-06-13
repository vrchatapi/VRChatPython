import vrcpy.objects as o
import vrcpy.types as types

## Avatar

class Avatar(o.Avatar):
    async def author(self):
        resp = await self.client.api.call("/users/"+self.authorId)
        self.client._raise_for_status(resp)
        return User(self.client, resp["data"])

## User

class LimitedUser(o.LimitedUser):
    async def public_avatars(self):
        '''
        Returns array of Avatar objects owned by user object
        '''

        resp = await self.client.api.call("/avatars",
            params={"userId": self.id})
        self.client._raise_for_status(resp)

        avatars = []
        for avatar in resp["data"]:
            avatars.append(Avatar(self.client, avatar))

        return avatars

class User(o.User, LimitedUser):
    async def public_avatars(self):
        avatars = await LimitedUser.public_avatars(self)
        return avatars

class CurrentUser(o.CurrentUser, User):
    obj = "CurrentUser"

    async def public_avatars(self):
        avatars = await User.public_avatars(self)
        return avatars

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

## World

class LimitedWorld(o.LimitedWorld):
    async def author(self):
        resp = await self.client.api.call("/users/"+self.authorId)
        self.client._raise_for_status(resp)
        return User(self.client, resp["data"])

class World(o.World, LimitedWorld):
    async def author(self):
        resp = await super(LimitedWorld, self).author()
        return resp

class Instance(o.Instance):
    async def world(self):
        resp = await self.client.api.call("/worlds/"+self.worldId)
        self.client._raise_for_status(resp)
        return World(resp["data"])
