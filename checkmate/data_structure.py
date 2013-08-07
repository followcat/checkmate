import collections

import zope.interface.interface

import checkmate.partition


def new_data_structure(name, parents, param):
    return type(name, parents, param)

def new_data_structure_interface(name, parents, param):
    return zope.interface.interface.InterfaceClass(name, parents, param)


class DataStructure(checkmate.partition.Partition):
    """"""

