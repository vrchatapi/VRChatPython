﻿class Model:
    __slots__ = ("loop")

    def __init__(self, loop, data):
        self.loop = loop

        for attr in data:
            setattr(self, self._fix_attr_name(attr), data[attr])

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