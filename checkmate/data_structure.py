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
        self.parameters = {}
        self.state = state 
        for argument in args:
            if argument.isalpha():
                self.parameters[argument] = None
        self.parameters.update(kwargs)

    def __eq__(self, other):
        """
            >>> DataStructure('AT1') == DataStructure('AT2')
            False
            >>> DataStructure('AT1') == DataStructure('AT1')
            True
        """
        if self.state == other.state:
            if (len(self.parameters) == 0 or len(other.parameters) == 0):
                return True
            elif (len(self.parameters) == len(other.parameters)):
                for key in iter(self.parameters):
                    if key not in iter(other.parameters):
                        return False
                    elif self.parameters[key] == other.parameters[key]:
                        return True
                    elif (self.parameters[key] is not None and
                        other.parameters[key] is not None):
                        return False
                return True
        return False

    def description(self):
        for key in list(self._description.keys()):
            if self == self._description[key][0].factory():
                return self._description[key][-1]
        return (None,None,None)

