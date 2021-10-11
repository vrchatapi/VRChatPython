from .errors import ClientErrors
from copy import deepcopy

def auth_required(method):
    async def _method(self, *args, **kwargs):
        logged_in = self.client._logged_in if hasattr(self, "client") else self._logged_in

        if not logged_in:
            raise ClientErrors.NotLoggedIn(
                "Client is not logged in!",
                method
            )

        resp = await method(self, *args, **kwargs)
        return resp

    ## Stuff for sphinx and autodocs
    _method.__doc__ = method.__doc__
    _method.__nested_annotations__ = method.__annotations__
    _method.__nested_module__ = method.__module__

    return _method