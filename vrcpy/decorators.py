def auth_required(method):
    async def _method(self, *args, **kwargs):
        logged_in = self.client._logged_in if hasattr(self, "client") else self._logged_in

        if not _logged_in:
            raise ClientErrors.NotLoggedIn(
                "Client is not logged in!",
                method
            )

        resp = await method(self, *args, **kwargs)
        return resp
    return _method