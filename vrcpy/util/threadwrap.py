import threading

class ThreadWrap(threading.Thread):
    def __init__(self, *args, start=True, **kwargs):
        kwargs["target"] = self._method
        super().__init__(*args, **kwargs)

        self.method = None
        self.daemon = True

    def _method(self):
        self.method()

    def set_method(self, method, *args, **kwargs):
        self.method = lambda: method(*args, **kwargs)