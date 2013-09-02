import zope.interface

import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IConnection)
class Client(object):
    """"""
    def __init__(self, name=None):
        """"""
        self.name = name

    def start(self):
        """"""

    def stop(self):
        """"""

    def send(self, exchange):
        """"""

    def read(self):
        """"""
        return []

    def received(self, exchange):
        """"""
        return False


#It is a Thread first given that Client is a dummy class for doctest purposes
class ThreadedClient(checkmate.runtime._threading.Thread, Client):
    """"""
    run_cycle_period = checkmate.runtime._threading.SLEEP_WHEN_RUN_SEC

    def __init__(self, name=None):
        """"""
        Client.__init__(self, name)
        checkmate.runtime._threading.Thread.__init__(self, name=name)


@zope.interface.implementer(checkmate.runtime.interfaces.IProtocol)
class Communication(object):
    """"""
    connection_handler = Client

    def initialize(self):
        """"""

    def close(self):
        """"""
