# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import zope.interface.interface

import checkmate.partition
import checkmate.interfaces


@zope.interface.implementer(checkmate.interfaces.IExchange)
class Exchange(checkmate.partition.Partition):
    """"""
    broadcast = False
    communication = ''

    def __init__(self, value=None, *args, default=True, origin='', destination='', **kwargs):
        """
            >>> import sample_app.application
            >>> r2 = sample_app.application.TestData.data_value['ActionRequest']['R2']
            >>> sorted(r2.items())
            [('C', 'AT2'), ('P', 'HIGH')]
            >>> ap = sample_app.exchanges.Action('AP', R=r2)
            >>> ap.R.C.value
            'AT2'
            >>> ap.R.P.value
            'HIGH'

        """
        super(Exchange, self).__init__(value, *args, default=default, **kwargs)
        self.origin_destination(origin, destination)
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

    def _dump(self):
        dump_dict = super()._dump()
        dump_dict['origin'] = self.origin
        dump_dict['destination'] = self.destination
        return dump_dict
        
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
            return checkmate.interfaces.IExchange.implementedBy(self.return_type)
        except AttributeError:
            return False

