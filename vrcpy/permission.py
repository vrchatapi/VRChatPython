from .model import Model

class Permission(Model):
    __slots__ = (
        "id", "name", "owner_id", "data"
    )