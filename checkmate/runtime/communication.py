import zope.interface


class IProtocol(zope.interface.Interface):
    """"""

class IConnection(zope.interface.Interface):
    """"""
    def startup(self):
        """"""

    def connect(self, server):
        """"""

@zope.interface.implementer(IConnection)
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


    def received(self, exchange):
        """"""
        return False


@zope.interface.implementer(IProtocol)
class Communication(object):
    """"""
    def initialize(self):
        """"""

