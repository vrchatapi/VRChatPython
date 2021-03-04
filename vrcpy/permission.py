from vrcpy.baseobject import BaseObject


class BasePermission(BaseObject):
    def __init__(self, client, loop=None):
        super().__init__(client, loop=loop)

        self.required.update({
            "id": {
                "dict_key": "id",
                "type": str
            },
            "data": {
                "dict_key": "data",
                "type": dict
            },
            "owner_id": {
                "dict_key": "ownerId",
                "type": str
            },
            "name": {
                "dict_key": "name",
                "type": str
            }
        })

    @staticmethod
    def build_permission(client, obj, loop=None):
        switch = {
            "permission-early-adopter-tags": EarlyAdopterPermission,
            "permission-extra-favorites-avatar-groups": ExtraFavoriteGroupPermission,
            "permission-supporter-tags": SupporterPermission,
            "permission-user-icons": UserIconPermission
        }

        return switch[obj["name"]](client, obj, loop)


class EarlyAdopterPermission(BasePermission):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop=loop)

        self._assign(obj)


class ExtraFavoriteGroupPermission:
    def __init__(self, client, obj=None, loop=None):
        super().__init__(client, loop=loop)

        self._assign(obj)

    def _assign(self, obj):
        super()._assign(obj)

        if "maxFavoriteGroups" in obj["data"]:
            for group in obj["data"]["maxFavoriteGroups"]:
                setattr(
                    self,
                    "max_%s_groups" % group,
                    obj["data"]["maxFavoriteGroups"][group]
                )

        if "maxFavoritesPerGroup" in obj["data"]:
            for group in obj["data"]["maxFavoriteGroups"]:
                setattr(
                    self,
                    "max_%ss_per_group" % group,
                    obj["data"]["maxFavoritesPerGroup"][group]
                )


class SupporterPermission(BasePermission):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop=loop)

        self._assign(obj)


class UserIconPermission(BasePermission):
    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop=loop)

        self._assign(obj)
