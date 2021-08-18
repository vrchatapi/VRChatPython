class RequestErrors:
    """Errors for vrcpy/request.py"""

    class NoSession(Exception):
        """Exception raised when no aiohttp session has been made and a call was made"""
        pass

    class SessionExists(Exception):
        """Exception raised when trying to make second new session without closing first"""
        pass

    class RequestError(Exception):
        """Exception raised when all request retry attempts fail"""
        pass

    class RateLimit(Exception):
        """Exception raised when received a 429 http response"""
        pass

    class Unauthorized(Exception):
        """Exception raised with regular 401 responses"""
        pass

    errors = [NoSession, SessionExists, RequestError, RateLimit, Unauthorized]


class VRChatErrors:
    """500 responses from VRChat"""

    class ServiceUnavailable(Exception):
        """Exception raised when 503 recieved"""
        pass


class ClientErrors:
    """Errors for vrcpy/client.py"""

    class OutOfDate(Exception):
        """Exception raised when apiKey is not in config"""
        pass

    class MissingCredentials(Exception):
        """Exception raised when Client.login is called without username+password"""
        pass

    class MfaRequired(Exception):
        """Exception raised when needing mfa code to login"""
        pass

    class MfaInvalid(Exception):
        """Exception raised when mfa code is invalid"""
        pass

    class InvalidEventFunction(Exception):
        """Exception raised when trying to apply vrcpy.Client.event decorator on a func with an invalid event name"""
        pass

    class InvalidAuthToken(Exception):
        """Exception raised when AuthToken isn't valid"""
        pass

    errors = [OutOfDate, MissingCredentials, MfaRequired, MfaInvalid,
              InvalidEventFunction, InvalidAuthToken]


class ObjectErrors:
    """Errors for vrcpy/objects.py"""

    class IntegretyError(Exception):
        """Exception raised when BaseObject._object_integrety fails"""
        pass

    class NotFriends(Exception):
        """Exception raised when user and current user aren't friends, and method requires them to be"""
        pass

    class AlreadyFriends(Exception):
        """Exception raised when user and current user are already friends"""
        pass

    class InvalidGroupName(Exception):
        """Exception raised when favorite group name is invalid"""
        pass

    class NotOwned(Exception):
        """Exception raised when operation performed on something unowned, and method requires it to be"""
        pass

    errors = [IntegretyError, NotFriends, AlreadyFriends, InvalidGroupName,
              NotOwned]
