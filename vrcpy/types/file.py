class FileVersion:
    __slots__ = (
        "version", "status", "created_at", "file", "delta", "signature"
    )

class FileAsset:
    __slots__ = (
        "file_name", "url", "md5", "size_in_bytes",
        "status", "category", "upload_id"
    )

class FileStatus:
    __slots__ = (
        "upload_id", "file_name", "next_part_number",
        "max_parts", "parts", "etags"
    )