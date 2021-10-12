from .rdict import RDict

class Announcement:
    __slots__ = ("name", "text")

    __types__ = RDict({
        "name": str,
        "text": str
    })

class DynamicWorldRow:
    __slots__ = (
        "index", "name", "platform", "sort_heading",
        "sort_order", "sort_ownership"
    )

    __types__ = RDict({
        "index": int,
        "name": str,
        "platform": str,
        "sort_heading": str,
        "sort_order": str,
        "sort_ownership": str
    })