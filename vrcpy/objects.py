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

        self._dict = {} # Dictionary that is assigned

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

        if hasattr(self, "__cinit__") and self.client.caching:
            if asyncio.iscoroutinefunction(self.__cinit__):
                self.cacheTask = asyncio.get_event_loop().create_task(self.__cinit__())
            else:
                self.__cinit__()

        self._dict = obj

    def _objectIntegrety(self, obj):
        if self.only == []:
            for key in self.unique:
                if not key in obj:
                    raise IntegretyError("Object does not have unique key ("+key+") for "+self.objType" (Class definition may be outdated, please make an issue on github)")
        else:
            for key in obj:
                if not key in self.only:
                    raise IntegretyError("Object has key not found in "+self.objType" (Class definition may be outdated, please make an issue on github)")
            for key in self.only:
                if not key in obj:
                    raise IntegretyError("Object does not have requred key ("+key+") for "+self.objType+" (Class definition may be outdated, please make an issue on github)")

## Avatar Objects

class Avatar(BaseObject):
    objType = "Avatar"

    def author(self):
        '''
        Used to get author of the avatar
        Returns User object
        '''

        resp = self.client.api.call("/users/"+self.authorId)
        return User(self.client, resp["data"])

    def favorite(self):
        '''
        Used to favorite avatar
        Returns favorite object
        '''

        resp = self.client.api.call("/favorites", "POST", json={"type": types.FavoriteType.Avatar,\
            "favoriteId": self.id, "tags": ["avatars1"]})
        return Favorite(self.client, resp["data"])

    def __init__(self, client, obj):
        super().__init__(client)
        self.unique += [
            "authorId",
            "authorName",
            "version",
            "name"
        ]

        self.arrTypes.update({
            "unityPackages": UnityPackage
        })

        self._assign(obj)

## User Objects

class LimitedUser(BaseObject):
    objType = "LimitedUser"

    def fetch_full(self):
        '''
        Used to get full version of this user
        Returns User object
        '''

        resp = self.client.api.call("/users/"+self.id)
        return User(self.client, resp["data"])

    def public_avatars(self):
        '''
        Used to get public avatars made by this user
        Returns list of Avatar objects
        '''

        resp = self.client.api.call("/avatars",
            params={"userId": self.id})

        avatars = []
        for avatar in resp["data"]:
            avatars.append(Avatar(self.client, avatar))

        return avatars

    def unfriend(self):
        '''
        Used to unfriend this user
        Returns void
        '''

        self.client.api.call("/auth/user/friends/"+self.id, "DELETE")

    def friend(self):
        '''
        Used to friend this user
        Returns Notification object
        '''

        resp = self.client.api.call("/user/"+self.id+"/friendRequest", "POST")
        return Notification(self.client, resp["data"])

    def favorite(self):
        '''
        Used to favorite this user
        Returns favorite object
        '''

        resp = self.client.api.call("/favorites", "POST", params={"type": types.FavoriteType.Friend,\
            "favoriteId": self.id})
        return Favorite(resp["data"])

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
        Used to get avatars by current user

            releaseStatus, string
            One of types type.ReleaseStatus

        Returns list of Avatar objects
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
        '''
        Used to update current user info

            email, string
            New email

            status, string
            New status

            statusDescription, string
            New website status

            bio, string
            New bio

            bioLinks, list of strings
            New links in bio

        Returns updated CurrentUser
        '''

        params = {"email": email, "status": status, "statusDescription": statusDescription,\
            "bio": bio, "bioLinks": bioLinks}

        for p in params:
            if params[p] == None: params[p] = getattr(self, p)

        resp = self.client.api.call("/users/"+self.id, "PUT", params=params)

        self.client.me = CurrentUser(self.client, resp["data"])
        return self.client.me

    def fetch_favorites(self, t):
        '''
        Used to get favorites

            t, string
            FavoriteType

        Returns list of Favorite objects
        '''

        resp = self.client.api.call("/favorites", params={"type": t})

        f = []
        for favorite in resp["data"]:
            f.append(Favorite(self.client, favorite))

        return f

    def remove_favorite(self, id):
        '''
        Used to remove a favorite via id

            id, string
            ID of the favorite object

        Returns void
        '''

        self.client.api.call("/favorites/"+id, "DELETE")

    def get_favorite(self, id):
        '''
        Used to get favorite via id

            id, string
            ID of the favorite object

        Returns Favorite object
        '''

        resp = self.client.api.call("/favorites/"+id)
        return Favorite(resp)

    def favorite(self):
        raise AttributeError("'CurrentUser' object has no attribute 'favorite'")

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
        else: self.homeLocation = None

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
        '''
        Used to get author of the world
        Returns User object
        '''

        resp = self.client.api.call("/users/"+self.authorId)
        return User(self.client, resp["data"])

    def favorite(self):
        '''
        Used to favorite this world object
        Returns Favorite object
        '''

        resp = self.client.api.call("/favorites", "POST", params={"type": types.FavoriteType.World,\
            "favoriteId": self.id})
        return Favorite(resp["data"])

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
        Used to get instance of this world via id

            id, string
            ID of instance

        Returns Instance object
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
        '''
        Used to get the world of this instance
        Returns World object
        '''

        resp = self.client.api.call("/worlds/"+self.worldId)
        return World(resp["data"])

    def short_name(self):
        '''
        Used to get shorturl of the instance
        Returns string
        '''

        return "https://vrchat.com/i/"+self.shortName

    def join(self):
        '''
        "Joins" the instance
        Returns void
        '''

        self.client.api.call("/joins", "PUT", json={"worldId": self.location.location})

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
