class RDict:
    __slots__ = ("_keys", "_values")

    def __init__(self, data: dict):
        self._keys = tuple(data.keys())
        self._values = tuple(data.values())

    def __getitem__(self, key):
        if key in self._keys:
            return self._values[self._keys.index(key)]
        raise KeyError(key)

    def __repr__(self):
        return "{" + ", ".join(
            ["%s: %s" % (self._keys[i], self._values[i]) for i in range(
                0, len(self._keys))]) + "}"

    def __contains__(self, key):
        return key in self._keys

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        for key in self._keys:
            yield key

    def keys(self):
        return self._keys

    def values(self):
        return iter(self._values)