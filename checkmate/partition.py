import builtins

import checkmate

class Partition(object):
    """"""
    partition_attribute = tuple()

    @classmethod
    @checkmate.fix_issue("checkmate/issues/default_type_in_exchange.rst")
    @checkmate.fix_issue("checkmate/issues/builtin_in_method_arguments.rst")
    def method_arguments(cls, arguments):
        """
            >>> import sample_app.application
            >>> import sample_app.exchanges
            >>> action = sample_app.exchanges.Action
            >>> action.method_arguments({'R': 'AT1'})
            {'R': 'AT1'}
            >>> action.method_arguments({'R': 'R2'})['R'].C.value, action.method_arguments({'R': 'R2'})['R'].P.value
            ('AT2', 'HIGH')
        """
        kwargs = dict(arguments)
        for attr, value in arguments.items():
            data_cls = cls._construct_values[attr]
            if hasattr(builtins, data_cls.__name__):
                kwargs[attr] = data_cls(value)
            else:
                for _s in data_cls.partition_storage.storage:
                    if _s.code == value:
                        kwargs[attr] = _s.factory()
                        break
                else:
                    if attr == value:
                        kwargs.pop(attr)
        return kwargs

    def __init__(self, value=None, *args, default=True, **kwargs):
        """
        The arguments are of str type, the values are stored in parameter dict.
            >>> e = Partition('CA', 'AUTO')
            >>> e.value
            'CA'

        If the partition defines an attribute as implementing IStorage, the factory() is called to instantiate the attribute.
            >>> import zope.interface
            >>> import checkmate.interfaces
            >>> import checkmate._storage
            >>> def factory(self): print("In factory")
            >>> A = type('A', (object,), {'factory': factory})
            >>> _impl = zope.interface.implementer(checkmate.interfaces.IStorage)
            >>> A = _impl(A)
            >>> setattr(Partition, 'A', A())
            >>> Partition.partition_attribute = ('A',)
            >>> ds = Partition('AT1')
            >>> delattr(Partition, 'A')
            >>> Partition.partition_attribute = tuple()

        Partition will be given a default value if none is provided.
        The default value is from definition in yaml:
            >>> import sample_app.application
            >>> re = sample_app.data_structure.ActionRequest()
            >>> re.C.value, re.P.value
            ('AT1', 'NORM')

        The default keyword only argument allow to use None as default:
            >>> import sample_app.application
            >>> re = sample_app.data_structure.ActionRequest(default=False)
            >>> re.C.value, re.P.value
            (None, None)
        """
        if type(value) == list:
            self.value = list(value)
        elif value == 'None':
            self.value = None
        else:
            self.value = value
            if value is None and default and hasattr(self, '_valid_values'):
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
            >>> r1.value = ['HIGH']
            >>> r1 == r2
            False
            >>> s1 = sample_app.component.component_1_states.State()
            >>> s2 = sample_app.component.component_1_states.State()
            >>> s1.value, s2.value
            (True, True)
            >>> s1 == s2
            True
            >>> s1.value = False
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

    def _dump(self):
        """
            >>> import sample_app.application
            >>> ac =sample_app.exchanges.Action('AC')
            >>> dump_dict = ac._dump()
            >>> dump_dict['value']
            'AC'
            >>> dump_dict['R']['C']['value']
            'AT1'
        """
        dump_dict = {}
        dump_dict['value'] = self.value
        for attr in self.partition_attribute:
            self_attr = getattr(self, attr)
            if isinstance(self_attr, Partition):
                dump_dict[attr] = self_attr._dump()
            else:
                dump_dict[attr] = self_attr
        return dump_dict

    def description(self):
        try:
            return (self.partition_storage.get_description(self))
        except AttributeError:
            return (None, None)

    def attribute_list(self, keyset=None):
        if keyset is None:
            return dict(map(lambda x:(x, getattr(self, x)), self.partition_attribute))
        else:
            return dict(map(lambda x:(x, getattr(self, x)), keyset.intersection(self.partition_attribute)))

    def carbon_copy(self, other):
        assert(type(self) == type(other))
        self.value = other.value
        for attr in self.partition_attribute:
            other_attr = getattr(other, attr)
            self_attr = getattr(self, attr)
            if isinstance(self_attr, Partition):
                self_attr.carbon_copy(other_attr)
            elif isinstance(other_attr, Partition):
                setattr(self, attr, type(other_attr)(**other_attr._dump()))

    @property
    def partition_id(self):
        return self.description()[0]

