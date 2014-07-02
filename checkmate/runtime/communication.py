import zope.interface

import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IProtocol)
class Connector(object):
    """"""
    def __init__(self, component=None, communication=None, is_server=False):
        self.component = component
        self.is_server = is_server
        self.communication = communication

    def initialize(self):
        """"""

    def open(self):
        """"""

    def close(self):
        """"""

    def send(self, exchange):
        """"""

    def receive(self):
        """"""


@zope.interface.implementer(checkmate.runtime.interfaces.ICommunication)
class Communication(object):
    """"""
    def __init__(self, component=None):
        """"""

    def initialize(self):
        """"""

    def start(self):
        """"""

    def close(self):
        """"""

