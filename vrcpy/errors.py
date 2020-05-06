class GeneralError(Exception):
    pass

class IncorrectLoginError(Exception):
    pass

class TwoFactorAuthNotSupportedError(Exception):
    pass

class AlreadyLoggedInError(Exception):
    pass

class IntegretyError(Exception):
    pass
