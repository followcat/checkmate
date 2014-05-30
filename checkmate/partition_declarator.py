import checkmate._exec_tools
import checkmate._module
import checkmate._storage
import checkmate.transition
import checkmate.parser.yaml_visitor


def _to_interface(_classname):
    return 'I' + _classname

def name_to_interface(name, modules):
    for _m in modules:
        if hasattr(_m, _to_interface(name)):
            interface = getattr(_m, _to_interface(name))
            break
    else:
        raise AttributeError(_m.__name__+' has no interface defined:'+_to_interface(name))
    return interface

def make_transition(item, exchanges, state_modules):
    initial_state = []
    input = []
    output = []
    final = []
    module_dict = { 'states':state_modules,
                    'exchanges':exchanges   }
    try:
        tran_name = item['name']
    except KeyError:
        tran_name = 'unknown'

    for _k, _v in item.items():
        if _k == 'initial' or _k == 'final':
            module_type = 'states'
        elif _k == 'incoming' or _k == 'outgoing':
            module_type = 'exchanges'
        elif _k == 'name':
            continue
        for each_item in _v:
            for _name, _data in each_item.items():
                interface = name_to_interface(_name, module_dict[module_type])
                storage_data = checkmate._storage.Data(module_type, interface, [_data])
                if _k == 'initial':
                    initial_state.append(storage_data)
                elif _k == 'final':
                    final.append(storage_data)
                elif _k == 'incoming':
                    input.append(storage_data)
                elif _k == 'outgoing':
                    output.append(storage_data)

    ts = checkmate._storage.TransitionStorage(checkmate._storage.TransitionData(initial_state, input, final, output))
    t = checkmate.transition.Transition(tran_name=tran_name, initial=ts.initial, incoming=ts.incoming, final=ts.final, outgoing=ts.outgoing)
    return t

class Declarator(object):
    def __init__(self, data_module, exchange_module, state_module=None,
                       transition_module=None, content=None):
        self.module = {}
        self.module['data_structure'] = data_module
        self.module['states'] = state_module
        self.module['exchanges'] = exchange_module

        self.basic_modules = {}
        self.basic_modules['data_structure'] = [data_module]
        self.basic_modules['states'] = [data_module]
        self.basic_modules['exchanges'] = [data_module, state_module]
        self.content = content
        if self.content is not None:
            self.data_source = checkmate.parser.yaml_visitor.call_visitor(self.content)
        self.output = {}

    def new_partition(self, partition_type, signature, codes_list, full_description=None):
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
        >>> par = de.new_partition('data_structure', "TestActionRequest", codes_list=[['D-PRIO-01', "P0('NORM')"]], full_description=collections.OrderedDict([("P0('NORM')",('D-PRIO-01', 'NORM valid value', 'NORM priority value'))]))
        >>> par  # doctest: +ELLIPSIS
        (<InterfaceClass checkmate.data.ITestActionRequest>, <checkmate._storage.PartitionStorage object at ...
        >>> par[1].get_description(checkmate.data.TestActionRequest('NORM'))
        ('D-PRIO-01', 'NORM valid value', 'NORM priority value')
        >>> sp = de.new_partition('states', "TestState", codes_list=["M0(True)"])
        >>> sp # doctest: +ELLIPSIS
        (<InterfaceClass checkmate.states.ITestState>, <checkmate._storage.PartitionStorage object at ...
        >>> ac = de.new_partition('exchanges', 'TestAction(R:TestActionRequest)', codes_list=[['X-ACTION-02', 'AP(R)']])
        >>> ac # doctest: +ELLIPSIS
        (<InterfaceClass checkmate.exchanges.ITestAction>, <checkmate._storage.PartitionStorage object at ...
        >>> ac[-1].storage[0].factory().R._valid_values
        [['NORM']]
        """
        _module = self.module[partition_type]
        defined_class, defined_interface = checkmate._module.exec_class_definition(self.basic_modules['data_structure'][0], partition_type, _module, signature, codes_list)
        codes = [_c[1] for _c in codes_list]
        partition_storage = checkmate._storage.PartitionStorage(partition_type, defined_interface, codes, full_description)
        setattr(defined_class, 'partition_storage', partition_storage)
        return (defined_interface, partition_storage)

    def new_transition(self, item):
        return make_transition(item, [self.module['exchanges']], [self.module['states']])

    def get_partitions(self):
        """
        >>> import os
        >>> import checkmate._module
        >>> import checkmate.application
        >>> import checkmate.partition_declarator
        >>> state_module = checkmate._module.get_module('checkmate.application', 'states')
        >>> exchange_module = checkmate._module.get_module('checkmate.application', 'exchanges')
        >>> data_structure_module = checkmate._module.get_module('checkmate.application', 'data')
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/exchanges.yaml'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> de = checkmate.partition_declarator.Declarator(data_structure_module, exchange_module, state_module=state_module, content=c)
        >>> de.get_partitions()
        >>> de.output['states']
        []
        >>> de.output['data_structure'] # doctest: +ELLIPSIS
        [(<InterfaceClass checkmate.data.ITESTActionRequest>, <checkmate._storage.PartitionStorage object at ...
        >>> de.output['exchanges'] # doctest: +ELLIPSIS
        [(<InterfaceClass checkmate.exchanges.ITESTAction>, <checkmate._storage.PartitionStorage object ...
        """
        for partition_type in ('states', 'data_structure', 'exchanges'):
            partitions = []
            for data in self.data_source[partition_type]:
                partitions.append(self.new_partition(partition_type, data['clsname'], data['codes_list'], data['full_desc']))
            self.output[partition_type] = partitions

    def get_transitions(self):
        """
        >>> import os
        >>> import checkmate._module
        >>> import checkmate.application
        >>> import checkmate.partition_declarator
        >>> state_module = checkmate._module.get_module('checkmate.application', 'states')
        >>> exchange_module = checkmate._module.get_module('checkmate.application', 'exchanges')
        >>> data_structure_module = checkmate._module.get_module('checkmate.application', 'data')
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/state_machine.yaml'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> de = checkmate.partition_declarator.Declarator(data_structure_module, exchange_module, state_module=state_module, content=c)
        >>> de.get_partitions()
        >>> de.get_transitions()
        >>> de.output['transitions'] # doctest: +ELLIPSIS
        [<checkmate.transition.Transition object at ...
        >>> len(de.output['transitions'])
        4
        """
        transitions = []
        for data in self.data_source['transitions']:
            transitions.append(self.new_transition(data))
        self.output['transitions'] = transitions

    def get_output(self):
        if self.content is not None:
            self.get_partitions()
            self.get_transitions()
            return self.output
