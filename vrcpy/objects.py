from vrcpy._hardtyping import *

from vrcpy import errors
from vrcpy import types

class BaseObject:
    objType = "Base"

    def __init__(self, client):
        self.unique = [] # Keys that identify this object
        self.only = [] # List of all keys in this object, if used
        self.types = {} # Dictionary of what keys have special types
        self.arrTypes = {} # Dictionary of what keys are arrays with special types
        self.client = client

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

    def _objectIntegrety(self, obj):
        if self.only == []:
            for key in self.unique:
                if not key in obj:
                    raise errors.IntegretyError("Object does not have unique key ("+key+") for "+self.objType)
        else:
            for key in obj:
                if not key in self.only:
                    raise errors.IntegretyError("Object has key not found in "+self.objType)
            for key in self.only:
                if not key in obj:
                    raise errors.IntegretyError("Object does not have requred key ("+key+") for "+self.objType)

## Avatar Objects

class Avatar(BaseObject):
    objType = "Avatar"

    def author(self):
        resp = self.client.api.call("/users/"+self.authorId)
        self.client._raise_for_status(resp)
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
        self.client._raise_for_status(resp)

        return User(self.client, resp["data"])

    def public_avatars(self):
        '''
        Returns array of Avatar objects owned by user object
        '''

        resp = self.client.api.call("/avatars",
            params={"userId": self.id})
        self.client._raise_for_status(resp)

        avatars = []
        for avatar in resp["data"]:
            avatars.append(Avatar(self.client, avatar))

        return avatars

    def unfriend(self):
        '''
        Returns void
        '''

        resp = self.client.api.call("/auth/user/friends/"+self.id, "DELETE")
        self.client._raise_for_status(resp)

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

    def avatars(self, releaseStatus=types.ReleaseStatus.All):
        '''
        Returns array of Avatar objects owned by the current user

            releaseStatus, string
            One of types type.ReleaseStatus
        '''

        resp = self.client.api.call("/avatars",
            params={"releaseStatus": releaseStatus, "user": "me"})
        self.client._raise_for_status(resp)

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
        self.client._raise_for_status(resp)

        self.client.me = CurrentUser(self.client, resp["data"])
        return self.client.me

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
        self.client._raise_for_status(resp)
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

    def __init__(self, client, obj):
        super().__init__(client)
        self.unique += [
            "namespace",
            "pluginUrl",
            "previewYoutubeId"
        ]

        self.arrTypes.update({
            "instances": Instance
        })

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
        self.client._raise_for_status(resp)
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
            "senderUserId",
            "seen",
            "details"
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
