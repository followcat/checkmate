# This code is part of the checkmate project.
# Copyright (C) 2013 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import collections

import zope.interface.interface

import checkmate.partition


def new_data_structure(name, parents, param):
    return type(name, parents, param)

def new_data_structure_interface(name, parents, param):
    return zope.interface.interface.InterfaceClass(name, parents, param)


class DataStructure(checkmate.partition.Partition):
    """"""

