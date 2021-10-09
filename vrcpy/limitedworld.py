from .model import Model

class LimitedWorld(Model):
    __slots__ = (
        "author_id", "author_name", "capacity", "created_at", "favorites",
        "heat", "id", "image_url", "labs_publication_date", "name",
        "occupants", "organization", "popularity", "publication_date",
        "release_status", "tags", "thumbnail_image_url", "unity_packages",
        "updated_at"
    )