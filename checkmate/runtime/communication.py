import zope.interface
import zope.component.factory

import checkmate.runtime.registry
import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IProtocol)
class Connector(object):
    """"""
    def __init__(self, component=None):
        self.component = component

    def stop(self):
        """"""


class Communication(object):
    """"""
    def __init__(self, default=False):
        self.default = default
        self.connector = Connector()

    def initialize(self):
        assert self.connector
        if self.default:
            checkmate.runtime.registry.global_registry.registerUtility(zope.component.factory.Factory(self.connector), zope.component.interfaces.IFactory, "default")
        else:
            checkmate.runtime.registry.global_registry.registerUtility(zope.component.factory.Factory(self.connector), zope.component.interfaces.IFactory)

    def close(self):
        """"""

