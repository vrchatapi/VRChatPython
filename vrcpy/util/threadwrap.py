import threading

class ThreadWrap(threading.Thread):
    """Internal class used to run non-coro events"""

    def __init__(self, method, *args, start=True, **kwargs):
        kwargs["target"] = lambda: method(*args, **kwargs)
        super().__init__(*args, **kwargs)

        self.daemon = True
        if start:
            self.start()
