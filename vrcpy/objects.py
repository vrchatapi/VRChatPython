from vrcpy import errors

class BaseObject:
    objType = "Base"

    def __init__(self):
        self.unique = [] # Keys that identify this object
        self.only = [] # List of all keys in this object, if used
        self.types = {} # Dictionary of what keys have special types
        self.arrTypes = {} # Dictionary of what keys are arrays with special types

    def _assign(self, obj):
        self._objectIntegrety(obj)

        for key in obj:
            if key in self.types:
                setattr(self, key, self.types[key](obj[key]))
            elif key in self.arrTypes:
                arr = []
                for o in obj[key]:
                    arr.append(self.arrTypes[key](o))
                setattr(self, key, arr)
            else:
                setattr(self, key, obj[key])

    def _objectIntegrety(self, obj):
        if self.only == []:
            for key in self.unique:
                if not key in obj:
                    raise errors.IntegretyError("Object does not have unique key for "+self.type)
        else:
            for key in obj:
                if not key in self.only:
                    raise errors.IntegretyError("Object has key not found in "+self.type)
            for key in self.only:
                if not key in obj:
                    raise errors.IntegretyError("Object does not have requred key for "+self.type)

## Avatar Objects

class Avatar(BaseObject):
    objType = "Avatar"

    def __init__(self, obj):
        super().__init__()
        self.unique += [
            "authorId",
            "imported",
            "version"
        ]

        self.arrTypes.update({
            "unityPackages": UnityPackage
        })

## User Objects

class LimitedUser(BaseObject):
    objType = "LimitedUser"

    def __init__(self, obj=None):
        super().__init__()
        self.unique += [
            "bio",
            "isFriend"
        ]

        if not obj == None: self._assign(obj)

class User(LimitedUser):
    objType = "User"

    def __init__(self, obj=None):
        super().__init__()
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

    def __init__(self, obj):
        super().__init__()
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

    def __init__(self, obj):
        super().__init__()
        self.only += [
            "twoFactorAuth"
        ]

        self._assign(obj)

class PastDisplayName(BaseObject):
    objType = "PastDisplayName"

    def __init__(self, obj):
        super().__init__()
        self.only += [
            "displayName",
            "updated_at"
        ]

        self._assign(obj)

# World objects

class LimitedWorld(BaseObject):
    objType = "LimitedWorld"

    def __init__(self, obj=None):
        super().__init__()
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

    def __init__(self, obj):
        super().__init__()
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

    def __init__(self, location):
        if not type(location) == str: raise TypeError("Expected string, got "+str(type(location)))

        self.nonce = None
        self.type = "public"
        self.name = ""
        self.worldId = None
        self.userId = None
        self.location = location

        if ":" in location:
            self.worldId, location = location.split(":")

        if "~" in location:
            self.name, location = location.split("~")
            parts = location.split("(")
            self.type = parts.pop(0)
            self.userId = parts.pop(0)[:-1]
            self.nonce = parts[0].split("(")[1].split(")")[0]
        else:
            self.name = location

class Instance(BaseObject):
    objType = "Instance"

    def __init__(self, obj):
        super().__init__()
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

    def __init__(self, obj):
        super().__init__()
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

    def __init__(self, obj):
        super().__init__()
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

    def __init__(self, obj):
        super().__init__()
        self.types.update({
            "worldId": Location
        })

        self._assign(obj)
