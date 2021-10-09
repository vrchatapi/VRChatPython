from .model import Model

class File(Model):
	__slots__ = (
		"id", "name", "owner_id", "mime_type",
		"extension", "tags", "versions"
	)