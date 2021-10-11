from ..model import Model
import time

class FileAsset(Model):
    __slots__ = (
        "file_name", "url", "md5", "size_in_bytes",
        "status", "category", "upload_id"
    )

    __types__ = {
        "file_name": str,
        "url": str,
        "md5": str,
        "size_in_bytes": int,
        "status": str,
    }

class FileVersion(Model):
    __slots__ = (
        "version", "status", "created_at", "file", "delta", "signature"
    )

    __types__ = {
        "version": int,
        "status": str,
        "created_at": time.struct_time,
        "file": FileAsset,
        "delta": FileAsset,
        "signature": FileAsset
    }

class FileStatus(Model):
    __slots__ = (
        "upload_id", "file_name", "next_part_number",
        "max_parts", "parts", "etags"
    )

    __types__ = {
        "upload_id": str,
        "file_name": str,
        "next_part_number": int,
        "max_parts": int,
        "parts": list,
        "etags": list
    }