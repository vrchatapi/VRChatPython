class ClientErrors:
    class NotLoggedIn(Exception):
        def __init__(self, message, callee):
            super().__init__(message)

            self.callee = callee