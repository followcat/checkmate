import functools

import zope.interface

import checkmate._utils
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

def get_procedure_transition(item, exchanges, state_modules):
    return make_transition(item, [exchanges], state_modules)[2]

def make_transition(item, exchanges, state_modules):
    initial_state = []
    input = []
    output = []
    final = []
    incoming_list = []
    outgoing_list = []
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
                    if interface not in incoming_list:
                        incoming_list.append(interface)
                elif _k == 'outgoing':
                    output.append(storage_data)
                    action = checkmate._utils.internal_code(_data)
                    if action not in outgoing_list:
                        outgoing_list.append(action)

    ts = checkmate._storage.TransitionStorage(checkmate._storage.TransitionData(initial_state, input, final, output))
    t = checkmate.transition.Transition(tran_name=tran_name, initial=ts.initial, incoming=ts.incoming, final=ts.final, outgoing=ts.outgoing)
    return (incoming_list, outgoing_list, t)

class Declarator(object):
    def __init__(self, data_module, state_module=None, exchange_module=None,
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

    def new_partition(self, partition_type, signature, standard_methods, codes, full_description=None):
        """
        >>> import sample_app.data_structure
        >>> import checkmate.exchange
        >>> import checkmate.state
        >>> import collections
        >>> import zope.interface
        >>> import checkmate.partition_declarator
        >>> de = checkmate.partition_declarator.Declarator(sample_app.data_structure, checkmate.state, checkmate.exchange)
        >>> par = de.new_partition('data_structure', "TestActionPriority", standard_methods = {}, codes=["P0('NORM')"], full_description=collections.OrderedDict([("P0('NORM')",('D-PRIO-01', 'NORM valid value', 'NORM priority value'))]))
        >>> par  # doctest: +ELLIPSIS
        (<InterfaceClass sample_app.data_structure.ITestActionPriority>, <checkmate._storage.PartitionStorage object at ...
        >>> par[1].get_description(sample_app.data_structure.TestActionPriority('NORM'))
        ('D-PRIO-01', 'NORM valid value', 'NORM priority value')
        >>> sp = de.new_partition('states', "TestState", standard_methods = {'toggle':getattr(checkmate.state, 'toggle')}, codes=["M0(True)"])
        >>> sp # doctest: +ELLIPSIS
        (<InterfaceClass checkmate.state.ITestState>, <checkmate._storage.PartitionStorage object at ...
        >>> ar = de.new_partition('data_structure', 'TestActionRequest(P=TestActionPriority)', standard_methods = {}, codes=[])
        >>> ar # doctest: +ELLIPSIS
        (<InterfaceClass sample_app.data_structure.ITestActionRequest>, <checkmate._storage.PartitionStorage object at ...
        >>> hasattr(ar[-1].storage[0].factory(), 'P')
        True
        >>> sample_app.data_structure.ITestActionPriority.providedBy(getattr(ar[-1].storage[0].factory(), 'P'))
        True
        >>> ac = de.new_partition('exchanges', 'TestAction(R=TestActionRequest)', standard_methods = {}, codes=['AP(R)'])
        >>> ac # doctest: +ELLIPSIS
        (<InterfaceClass checkmate.exchange.ITestAction>, <checkmate._storage.PartitionStorage object at ...
        >>> ac[-1].storage[0].factory().R.P.description()
        ('D-PRIO-01', 'NORM valid value', 'NORM priority value')
        """
        def set_partition_arguments(partition_type, standard_methods, key, value):
            partition_attribute = []
            for _module in self.basic_modules[partition_type]:
                try:
                    interface = getattr(_module, _to_interface(value))
                    standard_methods.update({key: checkmate._storage.store(partition_type, interface, value)})
                    partition_attribute.append(key)
                    break
                except AttributeError:
                    continue
            return partition_attribute

        def get_partition_attribute(signature, partition_type):
            partition_attribute = []
            for class_attr in checkmate._utils.method_arguments(signature).values:
                partition_attribute.extend(set_partition_arguments(partition_type, standard_methods, class_attr, class_attr))
            for key, class_kwattr in checkmate._utils.method_arguments(signature).attribute_values.items():
                partition_attribute.extend(set_partition_arguments(partition_type, standard_methods, key, class_kwattr[0][0]))
            return partition_attribute

        def set_standard_methods(_module, classname, codes, partition_attribute):
            standard_methods.update({'_valid_values': [checkmate._utils.valid_value_argument(_v) for _v in codes if checkmate._utils.valid_value_argument(_v) is not None],
                                     'partition_attribute': tuple(partition_attribute)})
            setattr(_module, classname, _module.declare(classname, standard_methods))
            setattr(_module, _to_interface(classname), _module.declare_interface(_to_interface(classname), {}))
            zope.interface.classImplements(getattr(_module, classname), [getattr(_module, _to_interface(classname))])

        def set_exchanges_codes(partition_type, _module, codes, cls):
            if partition_type == 'exchanges':
                for code in codes:
                    if checkmate._utils.is_method(code):
                        internal_code = checkmate._utils.internal_code(code)
                        setattr(_module, internal_code, functools.partial(cls, internal_code))

        partition_attribute = []
        classname = signature
        _module = self.module[partition_type]
        if checkmate._utils.is_method(signature):
            classname = checkmate._utils._leading_name(signature)
            partition_attribute = get_partition_attribute(signature, partition_type)
        set_standard_methods(_module, classname, codes, partition_attribute)

        interface = getattr(_module, _to_interface(classname))
        cls = checkmate._utils.get_class_implementing(interface)
        set_exchanges_codes(partition_type, _module, codes, cls)

        partition_storage = checkmate._storage.PartitionStorage(checkmate._storage.Data(partition_type, interface, codes, full_description))
        setattr(cls, 'partition_storage', partition_storage)

        return (interface, partition_storage)

    def new_transition(self, item):
        return make_transition(item, [self.module['exchanges']], [self.module['states']])

    def get_partitions(self):
        """
        >>> import sample_app.data_structure
        >>> import checkmate.exchange
        >>> import checkmate.state
        >>> import collections
        >>> import os
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/exchanges.yaml'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> de = checkmate.partition_declarator.Declarator(sample_app.data_structure, checkmate.state, checkmate.exchange, content=c) 
        >>> de.get_partitions()
        >>> de.output['states']
        []
        >>> de.output['data_structure'] # doctest: +ELLIPSIS
        [(<InterfaceClass sample_app.data_structure.ITESTAttribute>, <checkmate._storage.PartitionStorage object at ...
        >>> de.output['exchanges'] # doctest: +ELLIPSIS
        [(<InterfaceClass checkmate.exchange.ITESTAction>, <checkmate._storage.PartitionStorage object ...
        """
        for partition_type in ('states', 'data_structure', 'exchanges'):
            partitions = []
            for data in self.data_source[partition_type]:
                partitions.append(self.new_partition(partition_type, data['clsname'], data['standard_methods'], data['codes'], data['full_desc']))
            self.output[partition_type] = partitions

    def get_transitions(self):
        """
        >>> import sample_app.data_structure
        >>> import checkmate.exchange
        >>> import checkmate.state
        >>> import collections
        >>> import os
        >>> input_file = os.getenv("CHECKMATE_HOME") + '/checkmate/parser/state_machine.yaml'
        >>> f1 = open(input_file,'r')
        >>> c = f1.read()
        >>> f1.close()
        >>> de = checkmate.partition_declarator.Declarator(sample_app.data_structure, checkmate.state, checkmate.exchange, content=c) 
        >>> de.get_partitions()
        >>> de.get_transitions()
        >>> de.output['services']
        [<InterfaceClass checkmate.exchange.ITESTAction>]
        >>> de.output['transitions'] # doctest: +ELLIPSIS
        [<checkmate.transition.Transition object at ...
        >>> len(de.output['transitions'])
        4
        """
        transitions = []
        services = []
        outgoings = []
        for data in self.data_source['transitions']:
            _incomings, _outgoings, transition = self.new_transition(data)
            for _incoming in [ _i for _i in _incomings if _i not in services]:
                services.append(_incoming)
            for _outgoing in [ _i for _i in _outgoings if _i not in outgoings]:
                outgoings.append(_outgoing)
            transitions.append(transition)
        self.output['services'] = services
        self.output['outgoings'] = outgoings
        self.output['transitions'] = transitions

    def get_output(self):
        if self.content is not None:
            self.get_partitions()
            self.get_transitions()
            return self.output