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

        factory will set R = sample_app.data_structure.ActionRequest(['AT2', 'HIGH'])
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> ac = a.exchanges[0][-1].storage[0].factory(kwargs={'R':sample_app.data_structure.ActionRequest(['AT2', 'HIGH'])})
            >>> ac.R.value
            ['AT2', 'HIGH']

        We can define a partition by passing an instance for attribute.
            >>> re = sample_app.data_structure.ActionRequest(['AT2', 'HIGH'])
            >>> ac2 = a.exchanges[0][-1].storage[0].factory(kwargs={'R': re})
            >>> ac2.R.value
            ['AT2', 'HIGH']
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

    def get_partition_attr(self):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> ac = a.components['C1'].state_machine.transitions[0].incoming[0].factory()
            >>> dir(ac)
            ['R']
            >>> ac.get_partition_attr() #doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
            >>> dr = a.components['C2'].state_machine.transitions[3].incoming[0].factory()
            >>> dir(dr)
            []
            >>> dr.get_partition_attr()
            {}
        """
        _partition_dict = {}
        for attr in dir(self):
            _partition_dict[attr] = getattr(self, attr)
        return _partition_dict

    def __eq__(self, other):
        """
            >>> import sample_app.application
            >>> import sample_app.component.component_1_states
            >>> a = sample_app.application.TestData()
            >>> r1 = sample_app.exchanges.Action()
            >>> r2 = sample_app.exchanges.Action()
            >>> r1 == r2
            True
            >>> r1.value = ['HIGH']
            >>> r1 == r2
            False
            >>> s1 = sample_app.component.component_1_states.State()
            >>> s2 = sample_app.component.component_1_states.State()
            >>> s1.value, s2.value
            ('True', 'True')
            >>> s1 == s2
            True
            >>> s1.value = 'False'
            >>> s1 == s2
            False
        """
        if type(self) != type(other):
            return False
        if self.value is None:
            if len(dir(self)) == 0:
                return True
        elif other.value is None:
            if len(dir(other)) == 0:
                return True
        elif self.value == other.value:
            if (len(dir(self)) == 0 or len(dir(other)) == 0):
                return True
        else:
            return False
        if (len(dir(self)) == len(dir(other))):
            for key in iter(dir(self)):
                if key not in iter(dir(other)):
                    return False
                if (getattr(self, key) is not None and
                    getattr(other, key) is not None and
                    getattr(self, key) != getattr(other, key)):
                    return False
            return True
        return False

    def description(self):
        try:
            return (self.partition_storage.get_description(self))
        except AttributeError:
            return (None, None)

    @property
    def partition_id(self):
        return self.description()[0]

