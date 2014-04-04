import functools

import zope.interface

import checkmate._utils
import checkmate._storage
import checkmate.transition
import checkmate.parser.yaml_visitor


def _to_interface(_classname):
    return 'I'+_classname

def name_to_interface(name, module):
    try:
        interface = getattr(module, _to_interface(name))
    except AttributeError:
        raise AttributeError(module.__name__+' has no interface defined:'+_to_interface(name))
    return interface

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
        partition_attribute = []
        if checkmate._utils.is_method(signature):
            classname = checkmate._utils._leading_name(signature)
            for class_attr in checkmate._utils.method_arguments(signature).values:
                for _module in self.basic_modules[partition_type]:
                    try:
                        interface = getattr(_module, _to_interface(class_attr))
                        standard_methods.update({class_attr: checkmate._storage.store(partition_type, interface, class_attr)})
                        partition_attribute.append(class_attr)
                        break
                    except AttributeError:
                        continue
            for key, class_kwattr in checkmate._utils.method_arguments(signature).attribute_values.items():
                for _module in self.basic_modules[partition_type]:
                    try:
                        # class_kwattr[0][0] to get the classname from source string
                        interface = getattr(_module, _to_interface(class_kwattr[0][0]))
                        standard_methods.update({key: checkmate._storage.store(partition_type, interface, class_kwattr[0][0])})
                        partition_attribute.append(key)
                        break
                    except AttributeError:
                        continue
        else:
            classname = signature

        _module = self.module[partition_type]
        standard_methods.update({'_valid_values': [checkmate._utils.valid_value_argument(_v) for _v in codes if checkmate._utils.valid_value_argument(_v) is not None],
                                 'partition_attribute': tuple(partition_attribute)})
        setattr(_module, classname, _module.declare(classname, standard_methods))
        setattr(_module, _to_interface(classname), _module.declare_interface(_to_interface(classname), {}))
        zope.interface.classImplements(getattr(_module, classname), [getattr(_module, _to_interface(classname))])

        interface = getattr(_module, _to_interface(classname))
        cls = checkmate._utils.get_class_implementing(interface)
        for code in codes:
            if ((partition_type == 'exchanges') and (checkmate._utils.is_method(code))):
                setattr(_module, checkmate._utils.internal_code(code), functools.partial(cls, checkmate._utils.internal_code(code)))

        partition_storage = checkmate._storage.PartitionStorage(checkmate._storage.Data(partition_type, interface, codes, full_description))
        setattr(cls, 'partition_storage', partition_storage)

        # Return storage for compatibility only
        return (interface, partition_storage)

    def new_transition(self, item):
        initial_state = []
        input = []
        output = []
        final = []
        incoming_list = []
        outgoing_list = []

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
                    interface = name_to_interface(_name, self.module[module_type])
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

def get_procedure_transition(item, exchange_module, state_modules=[]):
    initial_state = []
    input = []
    final = []

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
                if module_type == 'states':
                    for s_module in state_modules:
                        if hasattr(s_module, _to_interface(_name)):
                            interface = name_to_interface(_name, s_module)
                            if _k == 'initial':
                                initial_state.append(checkmate._storage.Data(s_module, interface, [_data]))
                            elif _k == 'final':
                                final.append(checkmate._storage.Data(module_type, interface, [_data]))
                elif module_type == 'exchanges' and _k == 'incoming':
                    interface = name_to_interface(_name, exchange_module)
                    input.append(checkmate._storage.Data(module_type, interface, [_data]))

    ts = checkmate._storage.TransitionStorage(checkmate._storage.TransitionData(initial_state, input, final, []))
    return ts