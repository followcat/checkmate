import zope.interface.interface

import checkmate._utils
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

            >>> import checkmate._utils
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> args = checkmate._utils.ArgumentStorage(((), {'R': checkmate._utils.ArgumentStorage(((), {'P': checkmate._utils.ArgumentStorage((('HIGH',), {}))}))}))
            >>> ac = a.exchanges[0][-1].storage[0].factory(args.values, args.attribute_values)
            >>> ac.R.P.value
            'HIGH'
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
            if ((type(argument) == str) and (argument.isalpha())):
                self.parameters[argument] = None
        self.parameters.update(kwargs)

        for name in dir(self):
            attr = getattr(self, name)
            if name in iter(kwargs):
                if checkmate._utils.IArgumentStorage.providedBy(kwargs[name]):
                    attr = attr.factory(kwargs[name].values, kwargs[name].attribute_values)
                else:
                    # Fallback, for doctest mostly
                    attr = attr.factory((kwargs[name],))
            else:
                attr = attr.factory()
            setattr(self, name, attr)

    def __dir__(self):
        return self.partition_attribute

    def __eq__(self, other):
        """
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> r1 = a.data_structure[2][-1].storage[0].factory()
            >>> r2 = a.data_structure[2][-1].storage[0].factory()
            >>> r1 == r2
            True
            >>> r1.P.value
            'NORM'
            >>> r1.P.value = 'HIGH'
            >>> r1 == r2
            False
        """
        if type(self) != type(other):
            return False
        return compare_value(self, other) and compare_attr(self, other)


    def description(self):
        try:
            return (self.partition_storage.get_description(self))
        except AttributeError:
            return (None,None,None)

def compare_value(one, other):
    """
    >>> import checkmate.test_data
    >>> a = checkmate.test_data.App()
    >>> r1 = a.data_structure[1][-1].storage[0].factory()
    >>> r2 = a.data_structure[1][-1].storage[0].factory()
    >>> checkmate.partition.compare_value(r1, r2)
    True
    >>> r1.value
    'NORM'
    >>> r1.value = 'HIGH'
    >>> checkmate.partition.compare_value(r1, r2)
    False
    """
    if one._queue == True:
        if len(one.value) == 0:
            return (len(other.value) == 0 or other.value[0] == None)
        elif len(other.value) == 0:
            return (len(one.value) == 0 or one.value[0] == None)
        elif one.value[0] == None or other.value[0] == None:
            return True
        else:
            return (one.value == other.value)
    if one.value == None or other.value == None:
        return True
    else:
        return (one.value == other.value)

def compare_attr(one, other):
    """
    >>> import checkmate.test_data
    >>> a = checkmate.test_data.App()
    >>> r1 = a.data_structure[2][-1].storage[0].factory()
    >>> r2 = a.data_structure[2][-1].storage[0].factory()
    >>> checkmate.partition.compare_attr(r1, r2)
    True
    >>> r1.P.value
    'NORM'
    >>> r1.P.value = 'HIGH'
    >>> checkmate.partition.compare_attr(r1, r2)
    False
    """
    if type(one) != type(other):
        return False
    for name in dir(one):
        attr = getattr(one, name)
        if not (hasattr(other, name) and attr == getattr(other, name)):
            return False
    for name in dir(other):
        attr = getattr(other, name)
        if not (hasattr(one, name) and attr == getattr(one, name)):
            return False
    return True 

