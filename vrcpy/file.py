from vrcpy.baseobject import BaseObject


class FileBase(BaseObject):
    """Base file class that all file objects inherit from"""

    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop=loop)

        self.required.update({
            "extension": {
                "dict_key": "extension",
                "type": str
            },
            "id": {
                "dict_key": "id",
                "type": str
            },
            "mime_type": {
                "dict_key": "mimeType",
                "type": str
            },
            "name": {
                "dict_key": "name",
                "type": str
            },
            "owner_id": {
                "dict_key": "ownerId",
                "type": str
            },
            "versions": {
                "dict_key": "versions",
                "type": list
            }
        })

        self.optional.update({
            "tags": {
                "dict_key": "tags",
                "type": list
            }
        })

        self._assign(obj)

    @staticmethod
    def build_file(client, obj, loop=None):
        switch = {
            "icon": IconFile
        }

        if "tags" in obj and type(obj["tags"]) == list:
            for key in switch:
                if key in obj["tags"]:
                    return switch[key](client, obj, loop)

        return FileBase(client, obj, loop)


class File(BaseObject):
    """Represents a VRChat file"""

    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop=loop)

        self.required.update({
            "category": {
                "dict_key": "category",
                "type": str
            },
            "file_name": {
                "dict_key": "fileName",
                "type": str
            },
            "size_in_bytes": {
                "dict_key": "sizeInBytes",
                "type": int
            },
            "status": {
                "dict_key": "status",
                "type": str
            },
            "upload_id": {
                "dict_key": "uploadId",
                "type": str
            },
            "url": {
                "dict_key": "url",
                "type": str
            }
        })

        self._assign(obj)


class FileVersion(BaseObject):
    """Represents a version of a file"""

    def __init__(self, client, obj, loop=None):
        super().__init__(client, loop=loop)

        self.required.update({
            "created_at": {
                "dict_key": "created_at",
                "type": str
            },
            "status": {
                "dict_key": "status",
                "type": str
            },
            "version": {
                "dict_key": "version",
                "type": int
            }
        })

        self.optional.update({
            "file": {
                "dict_key": "file",
                "type": File
            }
        })

        self._assign(obj)


class IconFile(BaseObject):
    """Represents an icon"""
    pass
