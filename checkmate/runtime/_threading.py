import threading


#Only use this sleep time for thread who do *not* read on connection
TIMEOUT_LOCK_ACQUIRE = 1
SLEEP_WHEN_RUN_SEC = 0.05


class StopCondition(threading.Condition):
    def __init__(self):
        super(StopCondition, self).__init__()
        self.end = False

    def request(self):
        self.end = True

    def check(self):
        return self.end


class Thread(threading.Thread):
    """Thread class with stop mechanism.

    A child class should be derived.
    The run() method is not implemented.
    """
    def __init__(self, name=None):
        """"""
        super(Thread, self).__init__(name=name)
        self.stop_condition = StopCondition()


    def run(self):
        raise NotImplementedError()

    def check_for_stop(self):
        """Check if a stop request has been sent

        This should be called in the child run() method and run() should exit
        if check_for_stop() returns True
        """
        with self.stop_condition:
            output = self.stop_condition.wait_for(self.stop_condition.check, SLEEP_WHEN_RUN_SEC)
        return output

    def stop(self):
        """Send stop request

        Provided for the parent to stop the thread.
        """
        with self.stop_condition:
            self.stop_condition.request()
        self.join()

