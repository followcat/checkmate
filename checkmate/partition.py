import checkmate._storage


class Partition(object):
    """"""
    partition_attribute = tuple()

    def __init__(self, value=None, *args, **kwargs):
        """
        The arguments are of str type, the values are sotred in parameter dict.
            >>> e = Partition('CA', 'AUTO')
            >>> e.value
            'CA'

        If the partition defines an attribute as implementing IStorage, the factory() is called to instantiate the attribute.
            >>> import zope.interface
            >>> def factory(self): print("In factory")
            >>> A = type('A', (object,), {'factory': factory})
            >>> _impl = zope.interface.implementer(checkmate._storage.IStorage)
            >>> A = _impl(A)
            >>> setattr(Partition, 'A', A())
            >>> Partition.partition_attribute = ('A',)
            >>> ds = Partition('AT1')
            >>> delattr(Partition, 'A')
            >>> Partition.partition_attribute = tuple()

        factory will set R = sample_app.data_structure.ActionRequest('HIGH')
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> ac = a.exchanges[0][-1].storage[0].factory(kwargs={'R':sample_app.data_structure.ActionRequest('HIGH')})
            >>> ac.R.value
            'HIGH'

        We can define a partition by passing an instance for attribute.
            >>> re = sample_app.data_structure.ActionRequest('HIGH')
            >>> ac2 = a.exchanges[0][-1].storage[0].factory(kwargs={'R': re})
            >>> ac2.R.value
            'HIGH'
        """
        if type(value) == list:
            self.value = list(value)
        elif value == 'None':
            self.value = None
        else:
            self.value = value
            if value is None and hasattr(self, '_valid_values'):
                try:
                    self.value = self._valid_values[0]
                    if self.value == 'None':
                        self.value = None
                except:
                    pass
        for _k, _v in kwargs.items():
            setattr(self, _k, _v)

    def __dir__(self):
        return self.partition_attribute

    def __eq__(self, other):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> r1 = sample_app.exchanges.Action()
            >>> r2 = sample_app.exchanges.Action()
            >>> r1 == r2
            True
            >>> r1.R.value
            'NORM'
            >>> r1.R.value = 'HIGH'
            >>> r1 == r2
            False
        """
        if type(self) != type(other):
            return False
        return compare_value(self, other) and compare_attr(self, other)

    def get_define_str(self):
        """
            >>> import sample_app.application
            >>> ap = sample_app.exchanges.AP()
            >>> ap.partition_attribute
            ('R',)
            >>> ap.R.value
            'NORM'
            >>> ap.get_define_str() # doctest: +ELLIPSIS
            "R=sample_app.data_structure.ActionRequest(...
            >>> ex = sample_app.exchanges.ThirdAction()
            >>> ex.partition_attribute
            ()
            >>> ex.get_define_str()
            ''
        """
        if len(self.partition_attribute) == 0:
            if hasattr(self, 'action'):
                return ''
            if self.value is not None:
                return ''.join(("'", self.value, "'"))
        _str = ''
        for index, _attr_str in enumerate(self.partition_attribute):
            _attr = getattr(self, _attr_str)
            _cls = _attr.__class__
            _full_cls_str = '.'.join((_cls.__module__, _cls.__name__))
            if index > 0:
                _str += ', '
            _str = ''.join((_str, _attr_str, '=', _full_cls_str , '('))
            _str = ''.join((_str, _attr.get_define_str(), ')'))
        return _str

    def description(self):
        try:
            return (self.partition_storage.get_description(self))
        except AttributeError:
            return (None,None,None)

    @property
    def partition_id(self):
        return self.description()[0]

def compare_value(one, other):
    """
    >>> import sample_app.application
    >>> a = sample_app.application.TestData()
    >>> r1 = sample_app.data_structure.ActionRequest()
    >>> r2 = sample_app.data_structure.ActionRequest()
    >>> checkmate.partition.compare_value(r1, r2)
    True
    >>> r1.value
    'NORM'
    >>> r1.value = 'HIGH'
    >>> checkmate.partition.compare_value(r1, r2)
    False
    """
    if None in [one.value, other.value]:
        return True
    else:
        return one.value == other.value

def compare_attr(one, other):
    """
    >>> import checkmate.partition
    >>> import sample_app.application
    >>> a = sample_app.application.TestData()
    >>> r1 = sample_app.exchanges.Action()
    >>> r2 = sample_app.exchanges.Action()
    >>> checkmate.partition.compare_attr(r1, r2)
    True
    >>> r1.R.value
    'NORM'
    >>> r1.R.value = 'HIGH'
    >>> checkmate.partition.compare_attr(r1, r2)
    False
    """
    if ((type(one) != type(other)) or (len(dir(one)) != len(dir(other)))):
        return False
    for name in dir(one):
        attr = getattr(one, name)
        if not (hasattr(other, name) and attr == getattr(other, name)):
            return False
    # if dir(one) and dir(other) have same length and all elements of one is in other,
    # then *no* element of dir(other) is missing in dir(one)
    return True 

