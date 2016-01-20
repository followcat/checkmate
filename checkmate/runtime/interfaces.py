# This code is part of the checkmate project.
# Copyright (C) 2013-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import zope.interface


class ISut(zope.interface.Interface):
    """"""


class IStub(ISut):
    """"""
    def simulate(self, block):
        """"""

    def validate(self, block):
        """"""

