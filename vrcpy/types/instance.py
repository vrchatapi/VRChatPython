from ..model import Model

class Instance(Model):
    __slots__ = (
        "active", "can_request_invite", "capacity", "client_number", "full",
        "id", "instance_id", "location", "n_users", "name", "nonce",
        "owner_id", "permanent", "photon_region", "platforms", "region",
        "short_name", "tags", "type", "world_id"
    )