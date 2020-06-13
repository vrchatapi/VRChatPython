class GeneralError(Exception):
    ## General error
    pass

class IncorrectLoginError(Exception):
    ## When b64_auth is incorrect
    pass

class NotAuthenticated(Exception):
    ## When user tries to call authenticated requests without setting b64_auth
    pass

class TwoFactorAuthNotSupportedError(Exception):
    ## When trying to login with 2fa enabled account
    pass

class AlreadyLoggedInError(Exception):
    ## When trying to login when already logged in
    pass

class IntegretyError(Exception):
    ## When an object doesn't pass its integrety checks
    pass

class OutOfDateError(Exception):
    ## When api wrapper is too out of date to function at all
    pass

class NotFoundError(Exception):
    ## When a requested object doesn't exist
    pass

class NotFriendsError(Exception):
    ## When request requires users to be friends but they aren't
    pass
