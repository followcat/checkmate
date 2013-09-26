import zope.interface

import checkmate.runtime.client
import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IProtocol)
class Communication(object):
    """"""
    connection_handler = checkmate.runtime.client.Client

    def initialize(self):
        """"""

    def close(self):
        """"""
