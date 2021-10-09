from .model import Model

class User(Model):
    __slots__ = (
        "allow_avatar_copying", "bio", "bio_links",
        "current_avatar_image_url", "current_avatar_thumbnail_image_url",
        "date_joined", "developer_type", "display_name", "friend_key", "id",
        "instance_id", "is_friend", "last_login", "last_platform", "location",
        "location", "profile_pic_override", "state", "status",
        "status_description", "tags", "user_icon", "username", "world_id"
    )