import logging
import time

from .types.enum import PlayerModerationType, NotificationType

__basetypes__ = (
    str, int, list, dict, PlayerModerationType, NotificationType
)

class TypeCasts:
    @classmethod
    @property
    def __casts__(cls):
        return {
            time.struct_time: cls.struct_time
        }

    @staticmethod
    def struct_time(attr: str) -> time.struct_time:
        try:
            return time.strptime(attr, "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            return time.strptime(attr, "%Y-%m-%dT%H:%M:%S%z")

class Model:
    __slots__ = ("client", "loop")

    def __init__(self, client, data):
        self.client = client
        self.loop = self.client.loop

        logging.debug("Instantiating %s object" % self.__class__.__name__)

        for attr in data:
            fixed_attr = self._fix_attr_name(attr)
            setattr(self, fixed_attr, data[attr])
            self._fix_attr_type(fixed_attr)

    def _fix_attr_name(self, name):
        name_fin = ""
        for char in name:
            if char == char.upper() and char not in "_-":
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