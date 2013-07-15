import zope.interface.interface

import checkmate.state


def declare(name, param):
    return type(name, (checkmate.state.State,), param)

def declare_interface(name, param):
    return zope.interface.interface.InterfaceClass(name, (zope.interface.Interface,), param)

