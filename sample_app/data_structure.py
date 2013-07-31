import zope.interface.interface

import checkmate.data_structure


def declare(name, param):
    return type(name, (checkmate.data_structure.DataStructure,), param)

def declare_interface(name, param):
    return zope.interface.interface.InterfaceClass(name, (zope.interface.Interface,), param)

