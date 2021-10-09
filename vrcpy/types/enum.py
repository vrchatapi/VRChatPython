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