import zope.interface
import zope.component.factory

import checkmate.runtime.registry
import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IProtocol)
class Connector(object):
    """"""
    def __init__(self, component=None):
        self.component = component

    def open(self):
        """"""

    def close(self):
        """"""


@zope.interface.implementer(checkmate.runtime.interfaces.ICommunication)
class Communication(object):
    """"""
    def __init__(self):
        self.connector = Connector()

    def initialize(self):
        assert self.connector

    def close(self):
        """"""

