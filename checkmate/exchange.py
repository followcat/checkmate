import collections

import zope.interface.interface


def new_exchange(name, parents, param):
    return type(name, parents, param)

def new_exchange_interface(name, parents, param):
    return zope.interface.interface.InterfaceClass(name, parents, param)


class Exchange(object):
    """"""
    def __init__(self, action, *args, **kwargs):
        """
            >>> e = Exchange('CA', 'AUTO')
            >>> e.action
            'CA'
            >>> e.parameters['AUTO']
            >>> e = Exchange('CA', R=1)
            >>> e.parameters['R']
            1
        """
        self.parameters = {}
        self.action = action
        for argument in args:
            if argument.isalpha():
                self.parameters[argument] = None
        self.parameters.update(kwargs)

    def __eq__(self, other):
        """
            >>> Exchange('CA') == Exchange('TM')
            False
            >>> Exchange('CA') == Exchange('CA', R=2)
            True
            >>> Exchange('CA', R=1) == Exchange('CA', R=None)
            True
            >>> Exchange('CA', R=1) == Exchange('CA', R=2)
            False
            >>> Exchange('CA', R=1) == Exchange('CA', R0=1)
            False
        """
        if self.action == other.action:
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
        try:
            return (self.partition_storage.get_description(self))
        except AttributeError:
            return (None,None,None)

