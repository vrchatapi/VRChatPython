from .limiteduser import LimitedUser

class User(LimitedUser):
    __slots__ = (
        "allow_avatar_copying", "bio_links", "date_joined",
        "friend_key", "instance_id", "last_login", "location",
        "location", "state", "world_id"
    )