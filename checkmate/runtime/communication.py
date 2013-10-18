import zope.component.factory

import checkmate.runtime.registry


class Communication(object):
    """"""
    def __init__(self, default=False):
        self.default = default

    def initialize(self):
        assert self.connector
        if self.default:
            checkmate.runtime.registry.global_registry.registerUtility(zope.component.factory.Factory(self.connector), zope.component.interfaces.IFactory, "default")
        else:
            checkmate.runtime.registry.global_registry.registerUtility(zope.component.factory.Factory(self.connector), zope.component.interfaces.IFactory)

    def close(self):
        """"""
