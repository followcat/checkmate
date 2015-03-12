# This code is part of the checkmate project.
# Copyright (C) 2013 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import zope.interface
import zope.component.factory

import checkmate.runtime.registry
import checkmate.runtime.interfaces


@zope.interface.implementer(checkmate.runtime.interfaces.IProtocol)
class Connector(object):
    """"""
    def __init__(self, component=None):
        self.component = component

    def close(self):
        """"""


class Communication(object):
    """"""
    def __init__(self):
        self.connector = Connector()

    def initialize(self):
        assert self.connector

    def close(self):
        """"""

