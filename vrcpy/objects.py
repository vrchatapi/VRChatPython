from vrcpy._hardtyping import *

from vrcpy.errors import IntegretyError
from vrcpy import types

import asyncio

class BaseObject:
    objType = "Base"

    def __init__(self, client):
        self.unique = [] # Keys that identify this object
        self.only = [] # List of all keys in this object, if used
        self.types = {} # Dictionary of what keys have special types
        self.arrTypes = {} # Dictionary of what keys are arrays with special types
        self.client = client

        self.cacheTask = None # cacheTask for async objects using __cinit__

    def _assign(self, obj):
        self._objectIntegrety(obj)

        for key in obj:
            if key in self.types:
                setattr(self, key, self.types[key](self.client, obj[key]))
            elif key in self.arrTypes:
                arr = []
                for o in obj[key]:
                    arr.append(self.arrTypes[key](self.client, o))
                setattr(self, key, arr)
            else:
                setattr(self, key, obj[key])

        if hasattr(self, "__cinit__"):
            if asyncio.iscoroutinefunction(self.__cinit__):
                self.cacheTask = asyncio.get_event_loop().create_task(self.__cinit__())
            else:
                self.__cinit__()

    def _objectIntegrety(self, obj):
        if self.only == []:
            for key in self.unique:
                if not key in obj:
                    raise IntegretyError("Object does not have unique key ("+key+") for "+self.objType)
        else:
            for key in obj:
                if not key in self.only:
                    raise IntegretyError("Object has key not found in "+self.objType)
            for key in self.only:
                if not key in obj:
                    raise IntegretyError("Object does not have requred key ("+key+") for "+self.objType)

## Avatar Objects

class Avatar(BaseObject):
    objType = "Avatar"

    def author(self):
        resp = self.client.api.call("/users/"+self.authorId)
        return User(self.client, resp["data"])

    def __init__(self, client, obj):
        super().__init__(client)
        self.unique += [
            "authorId",
            "imported",
            "version"
        ]

        self.arrTypes.update({
            "unityPackages": UnityPackage
        })

        self._assign(obj)

## User Objects

class LimitedUser(BaseObject):
    objType = "LimitedUser"

    def fetch_full(self):
        resp = self.client.api.call("/users/"+self.id)
        return User(self.client, resp["data"])

    def public_avatars(self):
        '''
        Returns array of Avatar objects owned by user object
        '''

        resp = self.client.api.call("/avatars",
            params={"userId": self.id})

        avatars = []
        for avatar in resp["data"]:
            avatars.append(Avatar(self.client, avatar))

        return avatars

    def unfriend(self):
        '''
        Returns void
        '''

        resp = self.client.api.call("/auth/user/friends/"+self.id, "DELETE")

    def friend(self):
        '''
        Returns Notification object
        '''

        resp = self.client.api.call("/user/"+self.id+"/friendRequest", "POST")
        return Notification(self.client, resp["data"])

    def __init__(self, client, obj=None):
        super().__init__(client)
        self.unique += [
            "isFriend"
        ]

        if not obj == None: self._assign(obj)
        if not hasattr(self, "bio"): self.bio = ""

class User(LimitedUser):
    objType = "User"

    def __init__(self, client, obj=None):
        super().__init__(client)
        self.unique += [
            "allowAvatarCopying"
        ]

        self.types.update({
            "location": Location,
            "instanceId": Location
        })

        if not obj == None: self._assign(obj)

class CurrentUser(User):
    objType = "CurrentUser"

    def unfriend(self):
        raise AttributeError("'CurrentUser' object has no attribute 'unfriend'")

    def friend(self):
        raise AttributeError("'CurrentUser' object has no attribute 'friend'")

    def avatars(self, releaseStatus=types.ReleaseStatus.All):
        '''
        Returns array of Avatar objects owned by the current user

            releaseStatus, string
            One of types type.ReleaseStatus
        '''

        resp = self.client.api.call("/avatars",
            params={"releaseStatus": releaseStatus, "user": "me"})

        avatars = []
        for avatar in resp["data"]:
            if avatar["authorId"] == self.id:
                avatars.append(Avatar(self.client, avatar))

        return avatars

    def update_info(self, email=None, status=None,\
        statusDescription=None, bio=None, bioLinks=None):

        params = {"email": email, "status": status, "statusDescription": statusDescription,\
            "bio": bio, "bioLinks": bioLinks}

        for p in params:
            if params[p] == None: params[p] = getattr(self, p)

        resp = self.client.api.call("/users/"+self.id, "PUT", params=params)

        self.client.me = CurrentUser(self.client, resp["data"])
        return self.client.me

    def fetch_favorites(self, t):
        resp = self.client.api.call("/favorites", params={"type": t})

        f = []
        for favorite in resp["data"]:
            f.append(Favorite(self.client, favorite))

        return f

    def __cinit__(self):
        if hasattr(self, "currentAvatar"):
            self.currentAvatar = self.client.fetch_avatar(self.currentAvatar)

        self.onlineFriends = self.client.fetch_friends()
        self.offlineFriends = self.client.fetch_friends(offline=True)
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
            if self.homeLocation == "": self.homeLocation = None
            else: self.homeLocation = self.client.fetch_world(self.homeLocation)

    def __init__(self, client, obj):
        super().__init__(client)
        self.unique += [
            "feature",
            "hasEmail"
        ]

        self.types.update({
            "feature": Feature
        })

        self._assign(obj)

class Feature(BaseObject):
    objType = "Feature"

    def __init__(self, client, obj):
        super().__init__(client)
        self.only += [
            "twoFactorAuth"
        ]

        self._assign(obj)

class PastDisplayName(BaseObject):
    objType = "PastDisplayName"

    def __init__(self, client, obj):
        super().__init__(client)
        self.only += [
            "displayName",
            "updated_at"
        ]

        self._assign(obj)

# World objects

class LimitedWorld(BaseObject):
    objType = "LimitedWorld"

    def author(self):
        resp = self.client.api.call("/users/"+self.authorId)
        return User(self.client, resp["data"])

    def __init__(self, client, obj=None):
        super().__init__(client)
        self.unique += [
            "visits",
            "occupants",
            "labsPublicationDate"
        ]

        self.arrTypes.update({
            "unityPackages": UnityPackage
        })

        if not obj == None: self._assign(obj)

class World(LimitedWorld):
    objType = "World"

    def fetch_instance(self, id):
        '''
        Returns Instance object

            id, str
            InstanceID of instance
        '''

        resp = self.client.api.call("/instances/"+self.id+":"+id)
        return Instance(self.client, resp["data"])

    def __cinit__(self):
        instances = []
        for instance in self.instances:
            instances.append(self.fetch_instance(instance[0]))

        self.instances = instances

    def __init__(self, client, obj):
        super().__init__(client)

        self.unique += [
            "namespace",
            "pluginUrl",
            "previewYoutubeId",
            "instances"
        ]

        self._assign(obj)

class Location:
    objType = "Location"

    def __init__(self, client, location):
        if not type(location) == str: raise TypeError("Expected string, got "+str(type(location)))

        self.nonce = None
        self.type = "public"
        self.name = ""
        self.worldId = None
        self.userId = None
        self.location = location
        self.client = client

        if ":" in location:
            self.worldId, location = location.split(":")

        if "~" in location:
            self.name, t, nonce = location.split("~")
            self.type, self.userId = t.split("(")
            self.nonce = nonce.split("(")[1][:-1]
        else:
            self.name = location

class Instance(BaseObject):
    objType = "Instance"

    def world(self):
        resp = self.client.api.call("/worlds/"+self.worldId)
        return World(resp["data"])

    def short_name(self):
        return "https://vrchat.com/i/"+self.shortName

    def __init__(self, client, obj):
        super().__init__(client)
        self.unique += [
            "n_users",
            "instanceId",
            "shortName"
        ]

        self.types.update({
            "id": Location,
            "location": Location,
            "instanceId": Location,
        })

        self._assign(obj)

## unityPackage objects

class UnityPackage(BaseObject):
    objType = "UnityPackage"

    def __init__(self, client, obj):
        super().__init__(client)
        self.unique += [
            "id",
            "platform",
            "assetVersion",
            "unitySortNumber"
        ]

        self._assign(obj)

## Notification objects

class Notification(BaseObject):
    objType = "Notification"

    def __init__(self, client, obj):
        super().__init__(client)
        self.unique += [
            "senderUsername",
            "senderUserId"
        ]

        self.types.update({
            "details": NotificationDetails
        })

        self._assign(obj)

class NotificationDetails(BaseObject):
    objType = "NotificationDetails"

    def __init__(self, client, obj):
        super().__init__(client)
        self.types.update({
            "worldId": Location
        })

        self._assign(obj)

# Misc

class Favorite(BaseObject):
    objType = "Favorite"

    def __cinit__(self):
        if self.type == types.FavoriteType.World:
            self.object = self.client.fetch_world(self.favoriteId)
        elif self.type == types.FavoriteType.Friend:
            for friend in self.client.me.friends:
                if friend.id == self.favoriteId:
                    self.object = friend
                    break
        elif self.type == types.FavoriteType.Avatar:
            self.object = self.client.fetch_avatar(self.favoriteId)

    def __init__(self, client, obj):
        super().__init__(client)

        self.unique += [
            "id",
            "type",
            "favoriteId",
            "tags"
        ]

        self._assign(obj)
