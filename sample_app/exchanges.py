import zope.interface.interface

import checkmate.exchange


def declare(name, param):
    return type(name, (checkmate.exchange.Exchange,), param)

def declare_interface(name, param):
    return zope.interface.interface.InterfaceClass(name, (zope.interface.Interface,), param)

