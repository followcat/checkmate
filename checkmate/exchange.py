import zope.interface.interface

import checkmate.partition


class IExchange(zope.interface.Interface):
    """"""


@zope.interface.implementer(IExchange)
class Exchange(checkmate.partition.Partition):
    """"""
    def __init__(self, action=None, value=None, broadcast=False, *args, **kwargs):
        super(Exchange, self).__init__(value, *args, **kwargs)
        self._broadcast = broadcast
        self._action = action
        self._return_code = False

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
        if self.value == other.value and self.action == other.action:
            if (len(dir(self)) == 0 or len(dir(other)) == 0):
                return True
            elif (len(dir(self)) == len(dir(other))):
                for key in iter(dir(self)):
                    if key not in iter(dir(other)):
                        return False
                    if (getattr(self, key) is not None and
                        getattr(other, key) is not None and
                        getattr(self, key) != getattr(other, key)):
                        return False
                return True
        return False

    @property
    def action(self):
        """
            >>> e = Exchange('CA')
            >>> e.action
            'CA'
        """
        return self._action

    @property
    def broadcast(self):
        """
            >>> e = Exchange('CA')
            >>> e.broadcast
            False
        """
        return self._broadcast

    @property
    def return_code(self):
        """
            >>> e = Exchange('CA')
            >>> e.return_code
            False
        """
        return self._return_code

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

    @property
    def data_returned(self):
        """
            >>> Exchange().data_returned
            False
        """
        try:
            return IExchange.implementedBy(self.return_type)
        except AttributeError:
            return False

