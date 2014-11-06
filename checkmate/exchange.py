import zope.interface.interface

import checkmate.partition


class IExchange(zope.interface.Interface):
    """"""


@zope.interface.implementer(IExchange)
class Exchange(checkmate.partition.Partition):
    """"""
    def __init__(self, value=None, broadcast=False, *args, **kwargs):
        super(Exchange, self).__init__(value, *args, **kwargs)
        self._broadcast = broadcast

    def __eq__(self, other):
        """
        Now hasn't attribute:parameters,use dir() to get attribute.
            >>> import checkmate.exchange
            >>> checkmate.exchange.Exchange('CA') == checkmate.exchange.Exchange('TM')
            False
            >>> ca_1, ca_2 = checkmate.exchange.Exchange('CA'), checkmate.exchange.Exchange('CA', R=2)
            >>> ca_2.partition_attribute = ('R')
            >>> ca_1 == ca_2
            True
            >>> ca_1, ca_2 = checkmate.exchange.Exchange('CA', R=1), checkmate.exchange.Exchange('CA', R=None)
            >>> ca_1.partition_attribute = ('R')
            >>> ca_2.partition_attribute = ('R')
            >>> ca_1 == ca_2
            True
            >>> a_1, ca_2 = checkmate.exchange.Exchange('CA', R=1), checkmate.exchange.Exchange('CA', R=2)
            >>> ca_1.partition_attribute = ('R')
            >>> ca_2.partition_attribute = ('R')
            >>> ca_1 == ca_2
            False
            >>> a_1, ca_2 = checkmate.exchange.Exchange('CA', R=1), checkmate.exchange.Exchange('CA', R0=1)
            >>> ca_1.partition_attribute = ('R')
            >>> ca_2.partition_attribute = ('R0')
            >>> ca_1 == ca_2
            False
        """
        return super().__eq__(other)

    @property
    def broadcast(self):
        """
            >>> e = Exchange('CA')
            >>> e.broadcast
            False
        """
        return self._broadcast

    def origin_destination(self, origin, destination):
        self._origin = origin
        if type(destination) != list:
            self._destination = [destination]
        else:
            self._destination = destination

    @property
    def origin(self):
        """
            >>> e = Exchange()
            >>> e.origin_destination("origin","")
            >>> e.origin
            'origin'
        """
        try:
            return self._origin
        except AttributeError:
            return ""

    @property
    def destination(self):
        """
            >>> e = Exchange()
            >>> e.origin_destination("","destination")
            >>> e.destination
            ['destination']
        """
        try:
            return self._destination
        except AttributeError:
            return ""
