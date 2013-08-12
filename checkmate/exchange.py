import zope.interface.interface

import checkmate._storage
import checkmate.partition


def new_exchange(name, parents, param):
    return type(name, parents, param)

def new_exchange_interface(name, parents, param):
    return zope.interface.interface.InterfaceClass(name, parents, param)


class Exchange(checkmate.partition.Partition):
    """"""
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
        if self.value == other.value:
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

    @property
    def action(self):
        """
            >>> e = Exchange('CA')
            >>> e.action
            'CA'
        """
        return self.value

    def origin_destination(self, origin, destination):
        self._origin = origin
        self._destination = destination

    @property
    def origin(self):
        try:
            return self._origin
        except AttributeError:
            return ""

    @property
    def destination(self):
        try:
            return self._destination
        except AttributeError:
            return ""

