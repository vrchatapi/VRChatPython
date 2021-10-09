from .model import Model

class Avatar(Model):
    __slots__ = (
        "asset_url", "asset_url_object", "author_id", "author_name",
        "created_at", "description", "featured", "id", "image_url", "name",
        "release_status", "tags", "thumbnail_image_url", "unity_package_url",
        "unity_packages", "updated_at", "version"
    )