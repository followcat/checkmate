import collections

import zope.interface.interface


def new_data_structure(name, parents, param):
    return type(name, parents, param)

def new_data_structure_interface(name, parents, param):
    return zope.interface.interface.InterfaceClass(name, parents, param)


class DataStructure(object):
    """"""
    _default_description = (None, None, None)
    _description = {}
    def __init__(self, state, *args, **kwargs):
        """
            >>> ds = DataStructure('AT1')
            >>> ds.state
            'AT1'
        """
        self.state = state 
        self.args = args
        for key in list(kwargs.keys()):
            setattr(self, key, kwargs[key])

    def __eq__(self, other):
        """
            >>> DataStructure('AT1') == DataStructure('AT2')
            False
            >>> DataStructure('AT1') == DataStructure('AT1')
            True
        """
        if self.state[0] == None or other.state[0] == None:
            return True
        elif len(self.state) == 0:
            return (len(other.state) == 0)
        elif len(other.state) == 0:
            return (len(self.state))
        else:
            return (self.state == other.state)


    def description(self):
        for key in list(self._description.keys()):
            if self == self._description[key][0].factory():
                return self._description[key][-1]
        return (None,None,None)

