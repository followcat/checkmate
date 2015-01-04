import zope.interface

#from checkmate.exchange import IExchange
#from checkmate.runtime.component import IStub


class IRuntime(zope.interface.Interface):
    """"""
    def setup_environment(self, sut):
        """"""

    def start_test(self):
        """"""

    def stop_test(self):
        """"""


class IProtocol(zope.interface.Interface):
    """"""


class ICommunication(zope.interface.Interface):
    """"""
    def initialize(self):
        """"""

    def close(self):
        """"""


class IConnection(zope.interface.Interface):
    """"""
    def start(self):
        """"""

    def stop(self):
        """"""

    def send(self, exchange):
        """"""

    def read(self):
        """"""


class IProcedure(zope.interface.Interface):
    """"""
    exchange_list = zope.interface.Attribute("List of exchanges")

    def shortDescription(self):
        """"""

