class GeneralError(Exception):
    # General error
    pass


class IncorrectLoginError(Exception):
    # When b64_auth is incorrect
    pass


class NotAuthenticated(Exception):
    # When user tries to call authenticated requests without setting b64_auth
    pass


class RequiresTwoFactorAuthError(Exception):
    # When trying to login with 2fa enabled account without Client.login2fa()
    pass


class InvalidTwoFactorAuth(Exception):
    # When 2fa code passed for verification is incorrect
    pass


class AlreadyLoggedInError(Exception):
    # When trying to login when already logged in
    pass


class IntegretyError(Exception):
    # When an object doesn't pass its integrety checks
    pass


class OutOfDateError(Exception):
    # When api wrapper is too out of date to function at all
    pass


class NotFoundError(Exception):
    # When a requested object doesn't exist
    pass


class NotFriendsError(Exception):
    # When request requires users to be friends but they aren't
    pass


class AlreadyFriendsError(Exception):
    # When users are already friends
    pass


class WebSocketError(Exception):
    # When ws dies
    pass


class WebSocketOpenedError(Exception):
    # When 2 websockets are attempted to be open
    pass


class RateLimitError(Exception):
    # When VRChat is ratelimiting this user
    pass
