import collections

import zope.interface.interface


def new_data_structure(name, parents, param):
    return type(name, parents, param)

def new_data_structure_interface(name, parents, param):
    return zope.interface.interface.InterfaceClass(name, parents, param)


class DataStructure(object):
    """"""
    def __init__(self, state=None, *args, **kwargs):
        """
            >>> ds = DataStructure('AT1')
            >>> ds.state
            'AT1'
        """
        self.state = state 
        if state is None:
            try:
                self.state = self._valid_values[0]
            except:
                pass
            
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
        try:
            return (self.partition_storage.get_description(self))
        except AttributeError:
            return (None,None,None)

