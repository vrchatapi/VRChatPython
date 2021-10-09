class Announcement:
    __slots__ = ("name", "text")

    __types__ = {
        "name": str,
        "text": str
    }

class DynamicWorldRow:
    __slots__ = (
        "index", "name", "platform", "sort_heading",
        "sort_order", "sort_ownership"
    )

    __types__ = {
        "index": int,
        "name": str,
        "platform": str,
        "sort_heading": str,
        "sort_order": str,
        "sort_ownership": str
    }