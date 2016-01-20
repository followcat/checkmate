# This code is part of the checkmate project.
# Copyright (C) 2013-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import collections

import checkmate._storage
import checkmate._exec_tools


def make_partition(module,
                   items,
                   attributes={},
                   data_value={},
                   define_attributes={}):
    """"""
    partition_type = items['partition_type']
    signature = items['signature']
    codes_list = items['codes_list']
    values_list = items['values_list']
    try:
        full_description = items['full_description']
    except KeyError:
        full_description = None

    _module = module[partition_type]
    defined_class = checkmate._exec_tools.exec_class_definition(
                        module['data_structure'], partition_type,
                        _module, signature, values_list, attributes)
    code_arguments = collections.OrderedDict()
    for code, value in zip(codes_list, values_list):
        code_arguments[code] = {'value': value}
    if defined_class.__name__ in data_value:
        code_arguments.update(data_value[defined_class.__name__])
    partition_storage = checkmate._storage.PartitionStorage(
                            defined_class, code_arguments, full_description)
    setattr(defined_class, 'define_attributes', define_attributes)
    setattr(defined_class, 'partition_storage', partition_storage)
    return partition_storage


class Declarator(object):
    """"""
    data_value = {}

    def __init__(self, data_module, exchange_module,
                 state_module=None, data_value=None):
        self.module = {}
        self.module['data_structure'] = data_module
        self.module['states'] = state_module
        self.module['exchanges'] = exchange_module
        if data_value is not None:
            self.__class__.data_value = data_value

        self.output = {
            'data_structure': [],
            'states': [],
            'exchanges': []}

    @checkmate.fix_issue("checkmate/issues/new_partition_in_doctest.rst")
    def new_partition(self, items, attributes={}, define_attributes={}):
        """
        >>> import collections
        >>> import checkmate._module
        >>> import checkmate.application
        >>> import checkmate.data_structure
        >>> import checkmate.partition_declarator
        >>> state_module = checkmate._module.get_module(
        ...                    'checkmate.application', 'states')
        >>> exchange_module = checkmate._module.get_module(
        ...                       'checkmate.application', 'exchanges')
        >>> data_structure_module = checkmate._module.get_module(
        ...                             'checkmate.application', 'data')
        >>> de = checkmate.partition_declarator.Declarator(
        ...         data_structure_module,
        ...         exchange_module,
        ...         state_module=state_module)
        >>> items = {
        ...     'partition_type': 'data_structure',
        ...     'signature': "TestActionRequest",
        ...     'codes_list': ['TestActionRequestNORM'],
        ...     'values_list': ['NORM'],
        ...     'full_description': collections.OrderedDict(
        ...                         [('TestActionRequestNORM',
        ...                             ('D-PRIO-01',
        ...                              'NORM valid value',
        ...                              'NORM priority value'))])
        ...     }
        >>> de.new_partition(items)
        >>> output = de.get_output()
        >>> ds = output['data_structure']
        >>> ds[0].partition_class
        <class 'checkmate.data.TestActionRequest'>
        >>> ds[0].get_description(
        ...             checkmate.data.TestActionRequest('NORM'))
        ('D-PRIO-01', 'NORM valid value', 'NORM priority value')
        >>> items = {
        ...     'partition_type': 'states',
        ...     'signature': "TestState",
        ...     'codes_list': ['TestStateTrue'],
        ...     'values_list': [True],
        ...     }
        >>> de.new_partition(items)
        >>> dst = de.get_output()['states']
        >>> dst[0].partition_class
        <class 'checkmate.states.TestState'>
        >>> items = {
        ...     'partition_type': 'exchanges',
        ...     'signature': 'TestAction(R:TestActionRequest)',
        ...     'codes_list': ['AP(R)'],
        ...     'values_list': ['R'],
        ...     }
        >>> de.new_partition(items,
        ...     attributes={'communication':'test_comm'})
        >>> dee = de.get_output()['exchanges']
        >>> dee[0].partition_class
        <class 'checkmate.exchanges.TestAction'>
        >>> dee[0].storage[0].factory().R._valid_values
        ['NORM']
        >>> dee[0].storage[0].factory().communication
        'test_comm'
        """
        self.output[items['partition_type']].append(
            make_partition(
                self.module,
                items,
                attributes,
                self.__class__.data_value,
                define_attributes))

    def new_definitions(self, data_source):
        """
        >>> import collections
        >>> import checkmate._module
        >>> import checkmate.application
        >>> import checkmate.data_structure
        >>> import checkmate.partition_declarator
        >>> state_module = checkmate._module.get_module(
        ...                    'checkmate.application', 'states')
        >>> exchange_module = checkmate._module.get_module(
        ...                       'checkmate.application', 'exchanges')
        >>> data_structure_module = checkmate._module.get_module(
        ...                             'checkmate.application', 'data')
        >>> data_source = collections.OrderedDict([
        ... ('data_structure',[{
        ...     'signature': 'TestActionRequest',
        ...     'codes_list': ['TestActionRequestNORM'],
        ...     'values_list': ['NORM'],
        ...     'full_description': None,
        ...     'attributes': {},
        ...     'define_attributes': {}}]),
        ... ('states', [{
        ...    'signature': 'TestState',
        ...    'codes_list': ['TestStateTrue'],
        ...    'values_list': [True],
        ...    'full_description': None,
        ...    'attributes': {},
        ...    'define_attributes': {}}]),
        ... ('exchanges', [{
        ...    'signature': 'TestAction(R:TestActionRequest)',
        ...    'codes_list': ['AP(R)'],
        ...    'values_list': ['AP'],
        ...    'full_description': None,
        ...    'attributes': {},
        ...    'define_attributes': {}}])
        ... ])
        >>> de = checkmate.partition_declarator.Declarator(
        ...          data_structure_module,
        ...          exchange_module,
        ...          state_module=state_module)
        >>> de.new_definitions(data_source)
        >>> output = de.get_output()
        >>> output['data_structure'][0].partition_class
        <class 'checkmate.data.TestActionRequest'>
        >>> output['states'][0].partition_class
        <class 'checkmate.states.TestState'>
        >>> output['exchanges'][0].partition_class
        <class 'checkmate.exchanges.TestAction'>
        """
        for partition_type, chunk in data_source.items():
            for data in chunk:
                data['partition_type'] = partition_type
                self.new_partition(data, data['attributes'],
                    data['define_attributes'])

    def get_output(self):
        return self.output
