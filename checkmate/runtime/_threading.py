import threading

class Thread(threading.Thread):
    """Thread class with stop mechanism.

    A child class should be derived.
    The run() method is not implemented.
    """
    def __init__(self, name=None):
        """"""
        super(Thread, self).__init__(name=name)
        self.stop_lock = threading.Lock()
        self.end = False

    def run(self):
        raise NotImplementedError()

    def check_for_stop(self):
        """Check if a stop request has been sent

        This should be called in the child run() method and run() should exit
        if check_for_stop() returns True
        """

        result = True
        self.stop_lock.acquire()
        if not self.end:
            result = False
        self.stop_lock.release()
        return result

    def stop(self):
        """Send stop request

        Provided for the parent to stop the thread.
        """
        self.stop_lock.acquire(timeout=0.3)
        self.end = True
        self.stop_lock.release()

