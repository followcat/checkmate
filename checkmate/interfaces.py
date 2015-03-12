# This code is part of the checkmate project.
# Copyright (C) 2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import zope.interface


class IExchange(zope.interface.Interface):
    """"""


class IComponent(zope.interface.Interface):
    """"""


class IRun(zope.interface.Interface):
    """"""


class IState(zope.interface.Interface):
    """"""
    def append(self, *args, **kwargs):
        """"""

    def toggle(self, *args, **kwargs):
        """"""

    def flush(self, *args, **kwargs):
        """"""

    def up(self, *args, **kwargs):
        """"""

    def down(self, *args, **kwargs):
        """"""

    def pop(self, *args, **kwargs):
        """"""


class IStorage(zope.interface.Interface):
    """"""
    def factory(self, args=[], kwargs={}):
        """"""


class ITree(zope.interface.Interface):
    """"""

