from .limitedworld import LimitedWorld

class World(LimitedWorld):
    __slots__ = (
        "asset_url", "asset_url_obj", "description", "featured"
        "instance", "labs_publication_date", "name", "namespace",
        "plugin_url_object", "preview_youtube_id", "private_occupants",
        "public_occupants", "unity_package_url_object",
        "version", "visits"
    )