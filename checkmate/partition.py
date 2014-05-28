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
            >>> ac.R
            ['HIGH']

        We can define a partition by passing an instance for attribute.
            >>> re = sample_app.data_structure.ActionRequest('HIGH')
            >>> ac2 = a.exchanges[0][-1].storage[0].factory(kwargs={'R': re})
            >>> ac2.R
            ['HIGH']
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
            >>> import sample_app.component.component_1_states
            >>> a = sample_app.application.TestData()
            >>> r1 = sample_app.exchanges.Action()
            >>> r2 = sample_app.exchanges.Action()
            >>> r1 == r2
            True
            >>> r1.R
            ['NORM']
            >>> r1.R = ['HIGH']
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
        if None in [self.value, other.value]:
            return True
        return self.value==other.value

    def description(self):
        try:
            return (self.partition_storage.get_description(self))
        except AttributeError:
            return (None, None, None)

    @property
    def partition_id(self):
        return self.description()[0]

