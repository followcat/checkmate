import zope.interface

import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IProtocol)
class Communication(object):
    """"""
    def initialize(self):
        """"""

    def close(self):
        """"""
