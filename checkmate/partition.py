# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

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
            {}
            >>> action.method_arguments({'R': 'R2'})['R'].C.value
            'AT2'
            >>> action.method_arguments({'R': 'R2'})['R'].P.value
            'HIGH'
        """
        copy_arguments = dict(arguments)
        kwargs = dict(arguments)
        for attr, value in copy_arguments.items():
            data_cls = cls._construct_values[attr]
            if hasattr(builtins, data_cls.__name__):
                kwargs[attr] = data_cls(value)
                arguments.pop(attr)
            else:
                try:
                    kwargs[attr] = data_cls.storage_by_code(value).factory()
                    arguments.pop(attr)
                except AttributeError:
                    if type(value) != tuple:
                        kwargs.pop(attr)
        return kwargs

    @classmethod
    def storage_by_code(cls, code):
        for storage in cls.partition_storage.storage:
            if storage.code == code:
                return storage

    @classmethod
    def alike(cls, internal_storage, init_storage_list=None):
        """
        >>> import sample_app.application
        >>> state = sample_app.component.component_1_states.State
        >>> state.alike(sample_app.component.component_1.
        ... Component_1.engine.blocks[0].initial[0]).code
        'State1'
        """
        if init_storage_list is None:
            init_storage_list = list()
        for _s in cls.partition_storage.storage:
            if _s == internal_storage:
                return _s
        else:
            for _i in init_storage_list:
                if _i.partition_class == internal_storage.partition_class:
                    partition = internal_storage.factory(instance=_i.factory())
                    for _s in cls.partition_storage.storage:
                        if _s.value == partition.value:
                            return _s

    @checkmate.fix_issue("checkmate/issues/list_attribute_definition.rst")
    def __init__(self, value=None, *args, default=True, **kwargs):
        """
        The arguments are of str type, the values are stored in
        parameter dict.
            >>> e = Partition('CA', 'AUTO')
            >>> e.value
            'CA'

        If the partition defines an attribute as instance of Storage,
        the factory() is called to instantiate the attribute.
            >>> import checkmate._storage
            >>> def factory(self): print("In factory")
            >>> A = type('A', (object,), {'factory': factory})
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
            >>> re = sample_app.data_structure.ActionRequest(
            ...         default=False)
            >>> re.C.value, re.P.value
            (None, None)
        """
        if type(value) == list:
            self.value = list(value)
        elif value == 'None':
            self.value = None
        else:
            try:
                self.value = self.__class__.storage_by_code(value).value
            except AttributeError:
                self.value = value
            if (self.value is None and
                    default and hasattr(self, '_valid_values')):
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

