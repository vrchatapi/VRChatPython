from .model import Model

class LimitedUser(Model):
    __slots__ = (
        "bio", "current_avatar_image_url",
        "current_avatar_thumbnail_image_url", "developer_type",
        "display_name", "fallback_avatar", "id", "is_friend", "last_platform",
        "profile_pic_override", "status", "status_description", "tags",
        "user_icon", "username"
    )