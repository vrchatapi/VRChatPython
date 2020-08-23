import vrcpy.objects as o
import vrcpy.types as types

'''
Please look at objects.py for object docs
Everything is in the same place and does the same thing.

Thanks ~ Lazy me
'''

# Avatar


class Avatar(o.Avatar):
    async def author(self):
        resp = await self.client.api.call("/users/"+self.authorId)
        return User(self.client, resp["data"])

    async def favorite(self):
        resp = await self.client.api.call("/favorites", "POST", json={"type": types.FavoriteType.Avatar,
                                                                      "favoriteId": self.id, "tags": ["avatars1"]})

        f = Favorite(self.client, resp["data"])
        if self.client.caching:
            await f.cacheTask

        return f

    async def select(self):
        '''
        Selects this avatar to be used/worn
        '''

        await self.client.api.call("/avatars/{}/select".format(self.id), "PUT")

# User


class LimitedUser(o.LimitedUser):
    async def fetch_full(self):
        resp = await self.client.api.call("/users/"+self.id)
        return User(self.client, resp["data"])

    async def public_avatars(self):
        resp = await self.client.api.call("/avatars",
                                          params={"userId": self.id})

        avatars = []
        for avatar in resp["data"]:
            avatars.append(Avatar(self.client, avatar))

        return avatars

    async def unfriend(self):
        await self.client.api.call("/auth/user/friends/"+self.id, "DELETE")

    async def friend(self):
        resp = await self.client.api.call("/user/"+self.id+"/friendRequest", "POST")
        return o.Notification(self.client, resp["data"])

    async def favorite(self):
        resp = await self.client.api.call("/favorites", "POST", params={"type": types.FavoriteType.Friend,
                                                                        "favoriteId": self.id})
        return Favorite(resp["data"])


class User(o.User, LimitedUser):
    async def fetch_full(self):
        user = await LimitedUser.fetch_full(self)
        return user

    async def public_avatars(self):
        avatars = await LimitedUser.public_avatars(self)
        return avatars

    async def unfriend(self):
        await LimitedUser.unfriend()

    async def friend(self):
        notif = await LimitedUser.friend()
        return notif

    async def favorite(self):
        resp = await LimitedUser.favorite(self)
        return resp


class CurrentUser(o.CurrentUser, User):
    obj = "CurrentUser"

    async def fetch_full(self):
        user = await LimitedUser.fetch_full(self)
        return user

    async def public_avatars(self):
        avatars = await LimitedUser.public_avatars(self)
        return avatars

    async def unfriend(self):
        raise AttributeError("'CurrentUser' object has no attribute 'unfriend'")

    async def friend(self):
        raise AttributeError("'CurrentUser' object has no attribute 'friend'")

    async def update_info(self, email=None, status=None,
                          statusDescription=None, bio=None, bioLinks=None):

        params = {"email": email, "status": status, "statusDescription": statusDescription,
                  "bio": bio, "bioLinks": bioLinks}

        for p in params:
            if params[p] == None:
                params[p] = getattr(self, p)

        resp = await self.client.api.call("/users/"+self.id, "PUT", params=params)

        self.client.me = CurrentUser(self.client, resp["data"])
        return self.client.me

    async def avatars(self, releaseStatus=types.ReleaseStatus.All):
        resp = await self.client.api.call("/avatars",
                                          params={"releaseStatus": releaseStatus, "user": "me"})

        avatars = []
        for avatar in resp["data"]:
            if avatar["authorId"] == self.id:
                avatars.append(Avatar(self.client, avatar))

        return avatars

    async def fetch_favorites(self, t):
        resp = await self.client.api.call("/favorites", params={"type": t})

        f = []
        for favorite in resp["data"]:
            f.append(Favorite(self.client, favorite))

        if self.client.caching:
            for fav in f:
                await fav.cacheTask

        return f

    async def favorite(self):
        raise AttributeError("'CurrentUser' object has no attribute 'favorite'")

    async def remove_favorite(self, id):
        resp = await self.client.api.call("/favorites/"+id, "DELETE")

    async def fetch_favorite(self, id):
        resp = await self.client.api.call("/favorites/"+id)
        return Favorite(resp)

    async def __cinit__(self):
        if hasattr(self, "currentAvatar"):
            self.currentAvatar = await self.client.fetch_avatar(self.currentAvatar)

        self.onlineFriends = await self.client.fetch_friends()
        self.offlineFriends = await self.client.fetch_friends(offline=True)
        self.friends = self.onlineFriends + self.offlineFriends

        if hasattr(self, "activeFriends"):
            naf = []
            for fid in self.activeFriends:
                for f in self.friends:
                    if f.id == fid:
                        naf.append(f)
                        break

            self.activeFriends = naf

        if hasattr(self, "homeLocation"):
            if self.homeLocation == "":
                self.homeLocation = None
            else:
                self.homeLocation = await self.client.fetch_world(self.homeLocation)
        else:
            self.homeLocation = None

        # Wait for all cacheTasks
        if not self.homeLocation == None and self.client.caching:
            await self.homeLocation.cacheTask


class Feature(o.Feature):
    pass


class PastDisplayName(o.PastDisplayName):
    pass

# World


class LimitedWorld(o.LimitedWorld):
    async def author(self):
        resp = await self.client.api.call("/users/"+self.authorId)
        return User(self.client, resp["data"])

    async def favorite(self):
        resp = await self.client.api.call("/favorites", "POST", params={"type": types.FavoriteType.World,
                                                                        "favoriteId": self.id})
        return Favorite(resp["data"])


class World(o.World, LimitedWorld):
    async def author(self):
        resp = await super(LimitedWorld, self).author()
        return resp

    async def fetch_instance(self, id):
        resp = await self.client.api.call("/instances/"+self.id+":"+id)
        return Instance(self.client, resp["data"])

    async def favorite(self):
        resp = await LimitedWorld.favorite(self)
        return resp

    async def __cinit__(self):
        instances = []
        for instance in self.instances:
            instances.append(await self.fetch_instance(instance[0]))

        self.instances = instances


class Location(o.Location):
    pass


class Instance(o.Instance):
    async def world(self):
        resp = await self.client.api.call("/worlds/"+self.worldId)
        return World(resp["data"])

    async def join(self):
        await self.client.api.call("/joins", "PUT", json={"worldId": self.location})

# unityPackage objects


class UnityPackage(o.UnityPackage):
    pass

# Notification objects


class Notification(o.Notification):
    pass


class NotificationDetails(o.NotificationDetails):
    pass

# Misc


class Favorite(o.Favorite):
    async def __cinit__(self):
        if self.type == types.FavoriteType.World:
            self.object = await self.client.fetch_world(self.favoriteId)
        elif self.type == types.FavoriteType.Friend:
            for friend in self.client.me.friends:
                if friend.id == self.favoriteId:
                    self.object = friend
                    break
        elif self.type == types.FavoriteType.Avatar:
            self.object = await self.client.fetch_avatar(self.favoriteId)
