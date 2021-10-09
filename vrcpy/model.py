import time

from .types.enum import PlayerModerationType

__basetypes__ = (
    str, int, list, dict, PlayerModerationType
)

class TypeCasts:
    __casts__ = {
        time.struct_time: TypeCasts.struct_time
    }

    @staticmethod
    def struct_time(self, attr: str) -> time.struct_time:
        if attr == "created":
            return time.strptime(attr, "%Y-%m-%dT%H:%M:%S.%fZ")
        return time.strptime(attr, "%Y-%m-%dT%H:%M:%S%z")

class Model:
    __slots__ = ("client", "loop")

    def __init__(self, client, data):
        self.client = client
        self.loop = self.client.loop

        for attr in data:
            fixed_attr = self._fix_attr_name(attr)
            setattr(self, fixed_attr, data[attr])
            self._fix_attr_type(fixed_attr)

    def _fix_attr_name(self, name):
        name_fin = ""
        for char in name:
            if char == char.upper():
                if char == name[0]:
                    name_fin += char.lower()
                else:
                    name_fin += f"_{char.lower()}"
            else:
                name_fin += char
        return name_fin

    def _fix_attr_type(self, attr):
        if hasattr(self, "__types__") and attr in self.__types__:
            type_of = self.__types__[attr]

            if type_of in __basetypes__:
                setattr(self, attr, type_of(getattr(self, attr)))
            elif type_of in TypeCasts.__casts__:
                setattr(self, attr, TypeCasts.__casts__[type_of](
                    getattr(self, attr)))