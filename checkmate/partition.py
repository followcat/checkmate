import zope.interface.interface

import checkmate._storage


class Partition(object):
    """"""
    _queue = False
    partition_attribute = tuple()

    def __init__(self, value=None, *args, **kwargs):
        """
            >>> ds = Partition('AT1')
            >>> ds.value
            'AT1'

            >>> e = Partition('CA', 'AUTO')
            >>> e.value
            'CA'
            >>> e.parameters['AUTO']
            >>> e = Partition('CA', R=1)
            >>> e.parameters['R']
            1

            >>> import zope.interface
            >>> def factory(self): print("In factory")
            >>> A = type('A', (object,), {'factory': factory})
            >>> _impl = zope.interface.implementer(checkmate._storage.IStorage)
            >>> A = _impl(A)
            >>> setattr(Partition, 'A', A())
            >>> Partition.partition_attribute = ('A',)
            >>> ds = Partition('AT1')
            In factory
            >>> delattr(Partition, 'A')
            >>> Partition.partition_attribute = tuple()
        """
        if hasattr(self, 'append'):
            self._queue = True
        if self._queue == True:
            # intended to be a 'None' string
            if (type(value) == str and value == 'None'):
                value = []
            if type(value) == list:
                self.value = list(value)
            else:
                self.value = [value]
        else:
            self.value = value
            if value is None:
                try:
                    self.value = self._valid_values[0]
                except:
                    pass
            
        self.parameters = {}
        for argument in args:
            if argument.isalpha():
                self.parameters[argument] = None
        self.parameters.update(kwargs)

        for name in dir(self):
            attr = getattr(self, name)
            if checkmate._storage.IStorage.providedBy(attr):
                attr = attr.factory()
                setattr(self, name, attr)

    def __dir__(self):
        return self.partition_attribute

    def __eq__(self, other):
        """
            >>> Partition('AT1') == Partition('AT2')
            False
            >>> Partition('AT1') == Partition('AT1')
            True
        """
        if self._queue == True:
            if len(self.value) == 0:
                return (len(other.value) == 0 or other.value[0] == None)
            elif len(other.value) == 0:
                return (len(self.value) == 0 or self.value[0] == None)
            elif self.value[0] == None or other.value[0] == None:
                return True
            else:
                return (self.value == other.value)
        if self.value == None or other.value == None:
            return True
        else:
            return (self.value == other.value)

    def description(self):
        try:
            return (self.partition_storage.get_description(self))
        except AttributeError:
            return (None,None,None)

