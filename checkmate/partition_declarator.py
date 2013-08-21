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
                        standard_methods.update({class_attr: checkmate._storage.store(interface, class_attr)})
                        partition_attribute.append(class_attr)
                        break
                    except AttributeError:
                        continue
            for key, class_kwattr in checkmate._utils.method_arguments(signature).attribute_values.items():
                for _module in self.basic_modules[partition_type]:
                    try:
                        # class_kwattr[0][0] to get the classname from source string
                        interface = getattr(_module, _to_interface(class_kwattr[0][0]))
                        standard_methods.update({key: checkmate._storage.store(interface, class_kwattr[0][0])})
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

    def new_transition(self, array_items, tran_titles):
        component_transition = []
        initial_state = []
        initial_state_id = []
        row_count = len(array_items)
        for i in range(row_count):
            if array_items[i][1] != 'x':
                initial_state_id.append(i)
                if array_items[i][0] == 'x':
                    continue
                try:
                    interface = getattr(self.module['states'], _to_interface(array_items[i][0]))
                except AttributeError:
                    raise AttributeError(self.module['states'].__name__+' has no interface defined:'+_to_interface(array_items[i][0]))
                cls = checkmate._utils.get_class_implementing(interface)
                initial_state.append(checkmate._storage.store(interface, array_items[i][1]))
                if checkmate._utils.is_method(array_items[i][1]):
                    cls = checkmate._utils.get_class_implementing(interface)
                    setattr(self.module['states'], checkmate._utils.internal_code(array_items[i][1]),
                            functools.partial(cls, checkmate._utils.internal_code(array_items[i][1])))
        for i in range(2, len(array_items[0])):
            input = None
            for j in range(0, initial_state_id[0]):
                if array_items[j][i] != 'x':
                    try:
                        interface = getattr(self.module['exchanges'], _to_interface(array_items[j][0]))
                    except AttributeError:
                        raise AttributeError(self.module['exchanges'].__name__+' has no interface defined:'+_to_interface(array_items[j][0]))
                    input = checkmate._storage.store_exchange(interface, array_items[j][i])
            final = []
            for j in range(initial_state_id[0], initial_state_id[-1]+1):
                if array_items[j][0] == 'x':
                    continue
                try:
                    interface = getattr(self.module['states'], _to_interface(array_items[j][0]))
                except AttributeError:
                    raise AttributeError(self.module['states'].__name__+' has no interface defined:'+_to_interface(array_items[j][0]))
                final.append(checkmate._storage.store(interface, array_items[j][i]))
            output = []
            for j in range(initial_state_id[-1]+1, row_count):
                if array_items[j][i] != 'x':
                    try:
                        interface = getattr(self.module['exchanges'], _to_interface(array_items[j][0]))
                    except AttributeError:
                        raise AttributeError(self.module['exchanges'].__name__+' has no interface defined:'+_to_interface(array_items[j][0]))
                    output.append(checkmate._storage.store_exchange(interface, array_items[j][i]))
            try:
                tran_name = tran_titles[i]
            except IndexError:
                tran_name = 'unknown'
            t = checkmate.transition.Transition(tran_name=tran_name, initial=initial_state, incoming=input, final=final, outgoing=output)
            component_transition.append(t)
        return component_transition

