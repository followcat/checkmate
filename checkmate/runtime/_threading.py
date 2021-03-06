# This code is part of the checkmate project.
# Copyright (C) 2013-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import threading
import multiprocessing


class StopCondition(threading.Condition):
    def __init__(self):
        super(StopCondition, self).__init__()
        self.end = False

    def request(self):
        self.end = True

    def check(self):
        return self.end


class BaseClass(object):
    """"""
    def __init__(self):
        """"""
        self.stop_condition = StopCondition()

    def run(self):
        raise NotImplementedError()

    def check_for_stop(self):
        """Check if a stop request has been sent

        This should be called in the child run() method and run() should exit
        if check_for_stop() returns True
        """
        with self.stop_condition:
            return self.stop_condition.check()

    def stop(self):
        """Send stop request

        Provided for the parent to stop the thread.
        """
        with self.stop_condition:
            self.stop_condition.request()


class Thread(BaseClass, threading.Thread):
    """Thread class with stop mechanism.

    A child class should be derived.
    The run() method is not implemented.
    """
    def __init__(self, name=None):
        """"""
        super().__init__()
        threading.Thread.__init__(self, name=name)


class Process(BaseClass, multiprocessing.Process):
    """Process class with stop mechanism"""
    def __init__(self, name=None):
        """"""
        super().__init__()
        multiprocessing.Process.__init__(self, name=name)
        self.daemon = True

