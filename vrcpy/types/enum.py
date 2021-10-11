from enum import Enum

class UserStatus(Enum):
    """Status' users can set"""

    ACTIVE = "active"
    JOIN_ME = "join me"
    ASK_ME = "ask me"
    BUSY = "busy"
    OFFLINE = "offline"

class PlayerModerationType(Enum):
    """Moderation types"""

    MUTE = "mute"
    UNMUTE = "unmute"
    BLOCK = "block"
    UNBLOCK = "unblock"
    HIDEAVATAR = "hideAvatar"
    SHOWAVATAR = "showAvatar"

class DeveloperType(Enum):
    """User developer types"""

    NONE = "none"
    MODERATOR = "internal"

class NotificationType(Enum):
    """Types of notifications"""

    FRIEND_REQUEST = "friendRequest"
    INVITE = "invite"
    INVITE_RESPONSE = "inviteResponse"
    REQUEST_INVITE = "requestInvite"
    REQUEST_INVITE_RESPONSE = "requestInviteResponse"
    VOTE_TO_KICK = "votetokick"

class SearchGenericType(Enum):
    """Generic search types"""

    ALL = "all"

class ReleaseStatus(Enum):
    """Asset Release Status'"""

    PUBLIC = "public"
    PRIVATE = "private"
    HIDDEN = "hidden"

class Sort(Enum):
    """Search Sort Types"""

    POPULARITY = "popularity"
    HEAT = "heat"
    TRUST = "trust"
    SHUFFLE = "shuffle"
    RANDOM = "random"
    FAVORITES = "favorites"
    REPORT_SCORE = "reportScore"
    PUBLICATION_DATE = "publicationDate"
    LABS_PUBLICATION_DATE = "labsPublicationDate"
    CREATED = "created"
    UPDATED = "updated"
    ORDER = "order"
    RELEVANCE = "relevance"
    MAGIC = "magic"
    NAME = "name"

    CREATED_AT = "_created_at"
    UPDATED_AT = "_updated_at"

class SortOrder(Enum):
    """Order Sort Directions"""

    ASCENDING = "ascending"
    DESCENDING = "descending"

class UserFilter(Enum):
    """User Filter Types"""

    NONE = None
    ME = "me"

class FavoriteType(Enum):
    """Favorite Group Types"""

    WORLD = "world"
    AVATAR = "avatar"
    FRIEND = "friend"

class Visibility(Enum):
    """Visibility Types"""

    PRIVATE = "private"
    FRIENDS = "friends"
    PUBLIC = "public"