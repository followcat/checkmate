import functools

import zope.interface

import checkmate._utils
import checkmate._storage
import checkmate.transition


def _to_interface(_classname):
    return 'I'+_classname


class Declarator(object):
    def __init__(self, data_module, state_module=None, exchange_module=None,
                       transition_module=None):
        self.module = {}
        self.module['data_structure'] = data_module
        self.module['states'] = state_module
        self.module['exchanges'] = exchange_module

        self.basic_modules = {}
        self.basic_modules['data_structure'] = [data_module]
        self.basic_modules['states'] = [data_module]
        self.basic_modules['exchanges'] = [data_module, state_module]

    def new_partition(self, partition_type, signature, standard_methods, codes, full_description=None):
        """
        >>> import sample_app.data_structure
        >>> import sample_app.exchanges
        >>> import checkmate.state
        >>> import collections
        >>> import zope.interface
        >>> import checkmate.partition_declarator
        >>> de = checkmate.partition_declarator.Declarator(sample_app.data_structure, checkmate.state, sample_app.exchanges)
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
        (<InterfaceClass sample_app.exchanges.ITestAction>, <checkmate._storage.PartitionStorage object at ...
        >>> ac[-1].storage[0].factory().R.P.description()
        ('D-PRIO-01', 'NORM valid value', 'NORM priority value')
        """
        partition_attribute = []
        if checkmate._utils.is_method(signature):
            classname = checkmate._utils._leading_name(signature)
            for class_attr in checkmate._utils.method_arguments(signature)[0]:
                for _module in self.basic_modules[partition_type]:
                    try:
                        interface = getattr(_module, _to_interface(class_attr))
                        standard_methods.update({class_attr: checkmate._storage.store(interface, class_attr)})
                        partition_attribute.append(class_attr)
                        break
                    except AttributeError:
                        continue
            for key, class_kwattr in checkmate._utils.method_arguments(signature)[1].items():
                for _module in self.basic_modules[partition_type]:
                    try:
                        interface = getattr(_module, _to_interface(class_kwattr))
                        standard_methods.update({key: checkmate._storage.store(interface, class_kwattr)})
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

        partition_storage = checkmate._storage.PartitionStorage(partition_type, interface, codes, full_description)
        setattr(cls, 'partition_storage', partition_storage)

        # Return storage for compatibility only
        return (interface, partition_storage)

    def new_transition(self, array_items):
        component_transition = []
        initial_state = []
        initial_state_id = []
        row_count = len(array_items)
        for i in range(row_count):
            if array_items[i][1] != 'x':
                initial_state_id.append(i)
                if array_items[i][0] == 'x':
                    continue
                interface = getattr(self.module['states'], _to_interface(array_items[i][0]))
                cls = checkmate._utils.get_class_implementing(interface)
                initial_state.append((interface, array_items[i][1]))
                if checkmate._utils.is_method(array_items[i][1]):
                    cls = checkmate._utils.get_class_implementing(interface)
                    setattr(self.module['states'], checkmate._utils.internal_code(array_items[i][1]),
                            functools.partial(cls, checkmate._utils.internal_code(array_items[i][1])))
        for i in range(2, len(array_items[0])):
            input = []
            for j in range(0, initial_state_id[0]):
                if array_items[j][i] != 'x':
                    interface = getattr(self.module['exchanges'], _to_interface(array_items[j][0]))
                    input.append((interface, array_items[j][i]))
                    if self.module['exchanges'] is not None:
                        cls = checkmate._utils.get_class_implementing(interface)
                        setattr(self.module['exchanges'], checkmate._utils.internal_code(array_items[j][i]),
                                functools.partial(cls, checkmate._utils.internal_code(array_items[j][i])))
            final = []
            for j in range(initial_state_id[0], initial_state_id[-1]+1):
                if array_items[j][0] == 'x':
                    continue
                interface = getattr(self.module['states'], _to_interface(array_items[j][0]))
                final.append((interface, array_items[j][i]))
            output = []
            for j in range(initial_state_id[-1]+1, row_count):
                if array_items[j][i] != 'x':
                    interface = getattr(self.module['exchanges'], _to_interface(array_items[j][0]))
                    output.append((interface, array_items[j][i]))
                    if self.module['exchanges'] is not None:
                        cls = checkmate._utils.get_class_implementing(interface)
                        setattr(self.module['exchanges'], checkmate._utils.internal_code(array_items[j][i]),
                                functools.partial(cls, checkmate._utils.internal_code(array_items[j][i])))
            t = checkmate.transition.Transition(initial=initial_state, incoming=input, final=final, outgoing=output)
            component_transition.append(t)
        return component_transition
