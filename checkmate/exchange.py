import zope.interface.interface

import checkmate.partition


class IExchange(zope.interface.Interface):
    """"""


@zope.interface.implementer(IExchange)
class Exchange(checkmate.partition.Partition):
    """"""
    broadcast = False

    def __init__(self, value=None, *args, **kwargs):
        """
            >>> import sample_app.application
            >>> r2 = sample_app.application.TestData.data_value['R2']
            >>> sorted(r2['value'].items())
            [('C', 'AT2'), ('P', 'HIGH')]
            >>> ap = sample_app.exchanges.Action('AP', R=r2['value'])
            >>> ap.R.C.value
            'AT2'
            >>> ap.R.P.value
            'HIGH'

        """
        super(Exchange, self).__init__(value, *args, **kwargs)
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
        return super().__eq__(other)

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

