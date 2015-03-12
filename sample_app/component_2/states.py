# This code is part of the checkmate project.
# Copyright (C) 2013 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import zope.interface.interface

import checkmate.state


def declare(name, param):
    return type(name, (checkmate.state.State,), param)

def declare_interface(name, param):
    return zope.interface.interface.InterfaceClass(name, (zope.interface.Interface,), param)

