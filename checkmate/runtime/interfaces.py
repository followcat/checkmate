import zope.interface

#from checkmate.exchange import IExchange
#from checkmate.runtime.component import IStub


class IProcedure(zope.interface.Interface):
    """"""
    exchange_list = zope.interface.Attribute("List of exchanges")

    def shortDescription(self):
        """"""

