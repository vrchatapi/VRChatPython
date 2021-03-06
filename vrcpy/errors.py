class RequestErrors:
    # Errors for vrcpy/request.py

    class NoSession(Exception):
        # Raised when trying to make a call without a session
        pass

    class SessionExists(Exception):
        # Raised when trying to make second new session without closing first
        pass

    class RequestError(Exception):
        # Raised when all request retry attempts fail
        pass

    class RateLimit(Exception):
        # Raised when received a 429 http response
        pass

    class Unauthorized(Exception):
        # Raised with regular 401 responses
        pass

    errors = [NoSession, SessionExists, RequestError, RateLimit, Unauthorized]


class VRChatErrors:
    # 500 responses

    class ServiceUnavailable(Exception):
        # For 503
        pass


class ClientErrors:
    # Errors for vrcpy/client.py

    class OutOfDate(Exception):
        # Raised when apiKey is not in config
        pass

    class MissingCredentials(Exception):
        # Raised when Client.login is called without either username+password
        #   and base64
        pass

    class MfaRequired(Exception):
        # Raised when needing mfa code to login
        pass

    class MfaInvalid(Exception):
        # Raised when mfa code is invalid
        pass

    class InvalidEventFunction(Exception):
        # Raised when trying to @client.event a func without a valid event name
        pass

    class InvalidAuthToken(Exception):
        # Raised when AuthToken isn't valid
        pass

    errors = [OutOfDate, MissingCredentials, MfaRequired, MfaInvalid,
              InvalidEventFunction, InvalidAuthToken]


class ObjectErrors:
    # Errors for vrcpy/objects.py

    class IntegretyError(Exception):
        # Raised when BaseObject._object_integrety fails
        pass

    class NotFriends(Exception):
        # Raised when user and current user aren't friends
        pass

    class AlreadyFriends(Exception):
        # Raised when user and current user are already friends
        pass

    class InvalidGroupName(Exception):
        # Raised when group name is invalid
        pass

    class NotOwned(Exception):
        # Raised when operation performed on something unowned
        pass

    errors = [IntegretyError, NotFriends, AlreadyFriends, InvalidGroupName,
              NotOwned]
