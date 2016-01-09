# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

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

