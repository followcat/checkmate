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


@zope.interface.implementer(checkmate.runtime.interfaces.IProtocol)
class Communication(object):
    """"""
    connection_handler = Client

    def initialize(self):
        """"""

    def close(self):
        """"""
