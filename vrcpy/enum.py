from enum import Enum


class PlayerModerationType(Enum):
    BLOCK = "block"
    SHOW_AVATAR = "showAvatar"
    HIDE_AVATAR = "hideAvatar"
    MUTE = "mute"
    UNMUTE = "unmute"


class FavoriteType(Enum):
    WORLD = "world"
    FRIEND = "friend"
    AVATAR = "avatar"


class NotificationType(Enum):
    ALL = "all"
    FRIEND_REQUEST = "friendRequest"
    INVITE = "invite"
    REQUEST_INVITE = "requestInvite"
    REQUEST_INIVTE_RESPONSE = "requestInviteResponse"
    HIDDEN = "hidden"


class SortOrder(Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class SortType(Enum):
    CREATED = "created"
    UPDATED = "updated"
    ORDER = "order"

    _CREATED_AT = "_created_at"
    _UPDATED_AT = "_updated_at"


class ReleaseStatus(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    HIDDEN = "hidden"
    ALL = "all"
