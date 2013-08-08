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
    >>> checkmate.partition.compare_value(Partition('AT1'), Partition('AT1'))
    True
    >>> checkmate.partition.compare_value(Partition('AT1'), Partition('AT2'))
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
    >>> checkmate.partition.compare_attr(Partition('AT1'), Partition('AT2'))
    True
    >>> import checkmate.exchange
    >>> checkmate.partition.compare_attr(Partition('AT1'), checkmate.exchange.Exchange('R'))
    False
    >>> import sample_app.data_structure
    >>> import sample_app.exchanges 
    >>> import checkmate.state
    >>> import collections
    >>> import zope.interface
    >>> import checkmate.partition_declarator
    >>> de = checkmate.partition_declarator.Declarator(sample_app.data_structure, checkmate.state, sample_app.exchanges)
    >>> par = de.new_partition('data_structure', "TestActionPriority", standard_methods = {}, codes=["P0('NORM')", "P0('HIGH')"], full_description=collections.OrderedDict([("P0('NORM')",('D-PRIO-01', 'NORM valid value', 'NORM priority value')), ("P0('HIGH')",('D-PRIO-02', 'HIGH valid value', 'HIGH priority value'))]))
    >>> ar = de.new_partition('data_structure', 'TestActionRequest(P=TestActionPriority)', standard_methods = {}, codes=[], full_description=collections.OrderedDict())
    >>> c = ar[-1].storage[0].factory()
    >>> c1 = ar[-1].storage[0].factory()
    >>> c.P.value
    'NORM'
    >>> c1 == c
    True
    >>> c1.P.value = 'HIGH'
    >>> c1 == c
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

