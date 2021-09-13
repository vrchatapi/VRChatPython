import asyncio
import logging
from vrcpy.errors import ObjectErrors
from enum import EnumMeta


class BaseObject:
    """Base class that VRChat objects inherit from"""

    def __init__(self, client, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.client = client

        # "name": {"dict_key": "id", "type": str}
        self.required = {}
        self.optional = {}

    def _get_proper_obj(self, obj, t):
        if type(obj) is not t:
            if t is not dict and t is not list and t is not EnumMeta:
                return t(obj)
            elif t is EnumMeta:
                if type(obj) is str:
                    return t(obj.upper())
                else:
                    return t(obj)

        return obj

    def _assign(self, obj):
        logging.debug("Created %s object" % self.__class__.__name__)

        self._object_integrety(obj)
        self.raw = obj

        applied_keys = []

        for key in self.required:
            myobj = self._get_proper_obj(
                obj[self.required[key]["dict_key"]],
                self.required[key]["type"]
            )

            setattr(
                self,
                key,
                myobj
            )

            applied_keys.append(self.required[key]["dict_key"])

        for key in self.optional:
            if self.optional[key]["dict_key"] in obj:
                setattr(
                    self,
                    key,
                    self._get_proper_obj(
                        obj[self.optional[key]["dict_key"]],
                        self.optional[key]["type"]
                    )
                )
            else:
                setattr(self, key, None)

            applied_keys.append(self.optional[key]["dict_key"])

        for key in obj:
            if key not in applied_keys:
                attr_name = ""

                # Try auto-fix keys
                for char in key:
                    if char == char.upper() and not char.upper() == char.lower():
                        attr_name += "_" + char.lower()
                        continue

                    attr_name += char

                setattr(
                    self,
                    attr_name,
                    obj[key]
                )

        if hasattr(self, "__cinit__"):
            self.caching_finished = False
            self.cache_task = self.loop.create_task(self.__cinit__())

        # Save yo memory fool
        del self.required
        del self.optional
        del applied_keys

    def _object_integrety(self, obj):
        for key in self.required:
            if self.required[key]["dict_key"] not in obj:
                raise ObjectErrors.IntegretyError(
                    "{} object missing required key {}".format(
                        self.__class__.__name__, self.required[key]["dict_key"]
                    )
                )

    async def wait_for_cache(self):
        """Waits for any caching an object has to do"""

        if hasattr(self, "cache_task"):
            while not self.caching_finished:
                await asyncio.sleep(0.1)
