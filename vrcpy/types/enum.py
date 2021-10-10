from enum import Enum

class UserStatus(Enum):
    ACTIVE = "active"
    JOIN_ME = "join me"
    ASK_ME = "ask me"
    BUSY = "busy"
    OFFLINE = "offline"

class PlayerModerationType(Enum):
    MUTE = "mute"
    UNMUTE = "unmute"
    BLOCK = "block"
    UNBLOCK = "unblock"
    HIDEAVATAR = "hideAvatar"
    SHOWAVATAR = "showAvatar"

class NotificationType(Enum):
    FRIEND_REQUEST = "friendRequest"
    INVITE = "invite"
    INVITE_RESPONSE = "inviteResponse"
    REQUEST_INVITE = "requestInvite"
    REQUEST_INVITE_RESPONSE = "requestInviteResponse"
    VOTE_TO_KICK = "votetokick"