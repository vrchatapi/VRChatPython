class ClientErrors:
    class NotLoggedIn(Exception):
        def __init__(self, message, callee):
            super().__init__(message)

            self.callee = callee

    class MfaRequired(Exception):
        pass

    class MfaInvalid(Exception):
        pass

    class InvalidAuthToken(Exception):
        pass

class RequestErrors:
    class RateLimit(Exception):
        pass