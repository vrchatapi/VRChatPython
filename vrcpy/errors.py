class ClientErrors:
    class NotLoggedIn(Exception):
        """Exception raised when a method requiring login is called"""

        def __init__(self, message, callee):
            super().__init__(message)

            self.callee = callee

    class MfaRequired(Exception):
        """Exception raised when needing mfa code to login"""
        pass

    class MfaInvalid(Exception):
        """Exception raised when mfa code is invalid"""
        pass

    class InvalidAuthToken(Exception):
        """Exception raised when AuthToken isn’t valid"""
        pass

    class InvalidEventFunction(Exception):
        """
        Exception raised when trying to apply vrcpy.Client.event
        decorator on a func with an invalid event name
        """
        pass

class RequestErrors:
    class RateLimit(Exception):
        """Exception raised when received a 429 http response"""
        pass