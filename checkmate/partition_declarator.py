import checkmate._module
import checkmate._storage
import checkmate.transition
import checkmate._exec_tools
import checkmate.parser.yaml_visitor


def make_transition(items, exchanges, state_modules):
    module_dict = {'states': state_modules,
                   'exchanges': exchanges}
    try:
        tran_name = items['name']
    except KeyError:
        tran_name = 'unknown'

    ts = checkmate._storage.TransitionStorage(items, module_dict)
    t = checkmate.transition.Transition(tran_name=tran_name, initial=ts['initial'], incoming=ts['incoming'], final=ts['final'], outgoing=ts['outgoing'])
    return t


class Declarator(object):
    def __init__(self, data_module, exchange_module, state_module=None, transition_module=None, data_source=None):
        self.module = {}
        self.module['data_structure'] = data_module
        self.module['states'] = state_module
        self.module['exchanges'] = exchange_module

        self.data_source = data_source
        self.output = {
            'data_structure': [],
            'states': [],
            'exchanges': [],
            'transitions': []}

    @checkmate.report_issue("checkmate/issues/new_partition_in_doctest.rst")
    def new_partition(self, partition_type, signature, codes_list, values_list, code_value_list, full_description=None):
        """
        >>> import collections
        >>> import checkmate._module
        >>> import checkmate.application
        >>> import checkmate.data_structure
        >>> import checkmate.partition_declarator
        >>> state_module = checkmate._module.get_module('checkmate.application', 'states')
        >>> exchange_module = checkmate._module.get_module('checkmate.application', 'exchanges')
        >>> data_structure_module = checkmate._module.get_module('checkmate.application', 'data')
        >>> de = checkmate.partition_declarator.Declarator(data_structure_module, exchange_module, state_module=state_module)
        >>> de.new_partition('data_structure', "TestActionRequest", codes_list=['TestActionRequestNORM'], values_list=[['NORM']], code_value_list=[('TestActionRequestNORM', 'NORM')], full_description=collections.OrderedDict([('TestActionRequestNORM',('D-PRIO-01', 'NORM valid value', 'NORM priority value'))]))
        >>> de.get_output()['data_structure'][0]  # doctest: +ELLIPSIS
        (<InterfaceClass checkmate.data.ITestActionRequest>, <checkmate._storage.PartitionStorage object at ...
        >>> de.get_output()['data_structure'][0][1].get_description(checkmate.data.TestActionRequest('NORM'))
        ('D-PRIO-01', 'NORM valid value', 'NORM priority value')
        >>> de.new_partition('states', "TestState", codes_list=['TestStateTrue'], values_list=[["True"]], code_value_list=[('TestStateTrue', 'True')])
        >>> de.get_output()['states'][0] # doctest: +ELLIPSIS
        (<InterfaceClass checkmate.states.ITestState>, <checkmate._storage.PartitionStorage object at ...
        >>> de.new_partition('exchanges', 'TestAction(R:TestActionRequest)', codes_list=['AP(R)'], values_list=['AP'], code_value_list=[('AP(R)', 'AP')])
        >>> de.get_output()['exchanges'][0] # doctest: +ELLIPSIS
        (<InterfaceClass checkmate.exchanges.ITestAction>, <checkmate._storage.PartitionStorage object at ...
        >>> de.get_output()['exchanges'][0][-1].storage[0].factory().R._valid_values
        [['NORM']]
        """
        _module = self.module[partition_type]
        defined_class, defined_interface = checkmate._exec_tools.exec_class_definition(self.module['data_structure'], partition_type, _module, signature, codes_list, values_list)
        partition_storage = checkmate._storage.PartitionStorage(partition_type, defined_interface, code_value_list, full_description)
        setattr(defined_class, 'partition_storage', partition_storage)
        self.output[partition_type].append((defined_interface, partition_storage))

    def new_transition(self, item):
        self.output['transitions'].append(make_transition(item, [self.module['exchanges']], [self.module['states']]))

    def new_definitions(self):
        for partition_type, chunk in self.data_source.items():
            for data in chunk:
                if partition_type == 'transitions':
                    self.new_transition(data)
                else:
                    self.new_partition(partition_type, data['clsname'], data['codes_list'], data['values_list'], data['code_value_list'], data['full_desc'])

    def get_output(self):
        return self.output
