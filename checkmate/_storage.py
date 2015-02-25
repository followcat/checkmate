import zope.interface

import checkmate._module
import checkmate.transition
import checkmate.interfaces
import checkmate._exec_tools


def _to_interface(_classname):
    return 'I' + _classname

def name_to_interface(name, modules):
    for _m in modules:
        if hasattr(_m, _to_interface(name)):
            interface = getattr(_m, _to_interface(name))
            break
    else:
        raise AttributeError(
            _m.__name__ + ' has no interface defined:' + _to_interface(name))
    return interface


class Data(object):
    def __init__(self, interface, code_arguments, full_description=None):
        """
            >>> import checkmate._storage
            >>> import sample_app.application
            >>> import sample_app.exchanges
            >>> import sample_app.component.component_1_states
            >>> a = sample_app.application.TestData()
            >>> acr = sample_app.data_structure.ActionRequest()
            >>> acr #doctest: +ELLIPSIS
            <sample_app.data_structure.ActionRequest object at ...
            >>> c1_module = sample_app.component.component_1_states
            >>> data = checkmate._storage.Data(
            ...             c1_module.IAnotherState,
            ...             {'AnotherState1()': {'value': 'None'}})
            >>> state = data.storage[0].factory()
            >>> state.value
            >>> data = checkmate._storage.Data(
            ...         sample_app.exchanges.IAction, 
            ...         {'AP(R)': {'value': 'AP'}})
            >>> ex = data.storage[0].factory(R='HIGH')
            >>> (ex.value, ex.R.value)
            ('AP', 'HIGH')
        """
        self.type = type
        self.interface = interface
        self.full_description = full_description

        self.storage = []
        #n items for PartitionStorage and 1 item for TransitionStorage
        for code, arguments in code_arguments.items():
            try:
                code_description = self.full_description[code]
            except:
                code_description = (None, None)
            try:
                value = arguments.pop('value')
            except KeyError:
                value = None
            _storage = InternalStorage(self.interface, code, code_description,
                        value=value, arguments=arguments)
            self.storage.append(_storage)

    def get_description(self, item):
        """ Return description corresponding to item """
        for stored_item in list(self.storage):
            if item == stored_item.factory():
                return stored_item.description
        return (None, None)


class PartitionStorage(Data):
    """"""


class TransitionStorage(object):
    def __init__(self, items, module_dict):
        """"""
        super().__init__()
        self.name = ''
        self.final = []
        self.initial = []
        self.incoming = []
        self.outgoing = []
        self.returned = []

        for _k, _v in items.items():
            if _k == 'initial' or _k == 'final':
                module_type = 'states'
            elif _k == 'incoming' or _k == 'outgoing'or _k == 'returned':
                module_type = 'exchanges'
            elif _k == 'name':
                self.name = _v
                continue
            for each_item in _v:
                for _name, _data in each_item.items():
                    interface = \
                        name_to_interface(_name, module_dict[module_type])
                    code = checkmate._exec_tools.get_method_basename(_data)
                    define_class = \
                        checkmate._module.get_class_implementing(interface)
                    arguments = checkmate._exec_tools.get_signature_arguments(
                                    _data, define_class)
                    generate_storage = InternalStorage(interface, _data, None,
                                        arguments=arguments)
                    if _k == 'final':
                        generate_storage.function = define_class.__init__
                    for _s in define_class.partition_storage.storage:
                        if _s.code == code:
                            generate_storage.value = _s.value
                            break
                    else:
                        if hasattr(define_class, code):
                            generate_storage.function = \
                                getattr(define_class, code)
                    getattr(self, _k).append(generate_storage)

    def factory(self):
        return checkmate.transition.Transition(tran_name=self.name,
                                               initial=self.initial,
                                               incoming=self.incoming,
                                               final=self.final,
                                               outgoing=self.outgoing,
                                               returned=self.returned)


@zope.interface.implementer(checkmate.interfaces.IStorage)
class InternalStorage(object):
    """Support local storage of data (status or data_structure)
    information in transition"""
    def __init__(self, interface, code, description, value=None, arguments={}):
        """
            >>> import sample_app.application
            >>> import sample_app.exchanges
            >>> import checkmate._storage
            >>> st = checkmate._storage.InternalStorage(
            ...         sample_app.exchanges.IAction, "AP(R)",
            ...         None,
            ...         value="AP(R)")
            >>> [st.factory().R.C.value, st.factory().R.P.value]
            ['AT1', 'NORM']
        """
        self.origin_code = code
        self.code = checkmate._exec_tools.get_method_basename(code)
        self.description = description
        self.interface = interface
        self.cls = checkmate._module.get_class_implementing(interface)
        self.function = self.cls

        self.arguments = arguments
        self.resolved_arguments = self.function.method_arguments(arguments)
        self.key_to_resolve = frozenset(self.function._sig.parameters.keys())
        self.value = value

    @checkmate.fix_issue('checkmate/issues/init_with_arg.rst')
    @checkmate.fix_issue(
        'checkmate/issues/call_factory_without_resovle_arguments.rst')
    @checkmate.fix_issue(
        'checkmate/issues/factory_with_self_resolve_kw_arguments.rst')
    def factory(self, *args, instance=None, **kwargs):
        """
            >>> import sample_app.application
            >>> import sample_app.data_structure
            >>> import checkmate._storage
            >>> st = checkmate._storage.InternalStorage(
            ...         sample_app.exchanges.IAction,
            ...         "AP(R)", None, value="AP(R)")
            >>> [st.factory().R.C.value, st.factory().R.P.value]
            ['AT1', 'NORM']
            >>> st.factory(R=['AT2', 'HIGH']).R.value
            ['AT2', 'HIGH']

            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C1']
            >>> a.start()
            >>> i = sample_app.exchanges.Action('AP')
            >>> c.process([i])[-1] # doctest: +ELLIPSIS
            <sample_app.exchanges.ThirdAction object at ...
            >>> i = sample_app.exchanges.Action('AC')
            >>> c.process([i]) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> c.states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object ...
            >>> t = c.state_machine.transitions[2]
            >>> i = t.incoming[0].factory(); i.value
            'PP'
            >>> t.final[1].function # doctest: +ELLIPSIS
            <function State.pop at ...
            >>> arguments = t.final[1].resolve(exchanges=[i])
            >>> t.final[1].factory(instance=c.states[1],
            ...     **arguments) # doctest: +ELLIPSIS
            <sample_app.component.component_1_states.AnotherState ...
            >>> c.states[1].value
            []
        """
        if 'default' not in kwargs or kwargs['default']:
            if len(args) == 0:
                args = (self.value, )
            if len(kwargs) == 0:
                kwargs.update(self.resolved_arguments)
        if instance is not None and self.interface.providedBy(instance):
            try:
                value = self.value
            except IndexError:
                value = None
            self.function(instance, value, **kwargs)
            return instance
        else:
            return self.function(*args, **kwargs)

    @checkmate.fix_issue("checkmate/issues/transition_resolve_arguments.rst")
    def resolve(self, states=None, exchanges=None, resolved_dict={}):
        """
            >>> import sample_app.application
            >>> import sample_app.exchanges
            >>> import checkmate._storage
            >>> a = sample_app.application.TestData()
            >>> t = a.components['C1'].state_machine.transitions[1]
            >>> inc = t.incoming[0].factory()
            >>> states = [t.initial[0].factory()]
            >>> t.final[0].resolve(states)
            {'R': None}
            >>> t.final[0].resolve(exchanges=[inc]) # doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
            >>> inc = t.incoming[0].factory(R=['AT2', 'HIGH'])
            >>> inc.R.value
            ['AT2', 'HIGH']
            >>> t.final[0].resolve(exchanges=[inc]) # doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
            >>> inc = t.incoming[0].factory(R=1)
            >>> (inc.value, inc.R.value)  # doctest: +ELLIPSIS
            ('AP', 1)
            >>> t.final[0].resolve(exchanges=[inc]) # doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
            >>> module_dict = {
            ...     'states': [sample_app.component.component_1_states],
            ...     'exchanges':[sample_app.exchanges]}
            >>> item = {'name': 'Toggle TestState tran01',
            ...         'outgoing': [{'Action': 'AP(R2)'}],
            ...         'incoming': [{'AnotherReaction': 'ARE()'}]}
            >>> ts = checkmate._storage.TransitionStorage(
            ...         item, module_dict)
            >>> t = ts.factory()
            >>> t.outgoing[0].resolved_arguments['R'].C.value
            'AT2'
            >>> t.outgoing[0].resolved_arguments['R'].P.value
            'HIGH'
            >>> t.outgoing[0].value
            'AP'
            >>> resolved_arguments = t.outgoing[0].resolve()
            >>> list(resolved_arguments.keys())
            ['R']
            >>> resolved_arguments['R'].C.value 
            'AT2'
            >>> resolved_arguments['R'].P.value
            'HIGH'
        """
        if states is None:
            states = []
        if exchanges is None:
            exchanges = []
        _attributes = {}
        for attr in self.cls._construct_values.keys():
            if (attr in self.arguments and
                    type(self.arguments[attr]) != tuple and
                    self.arguments[attr] in resolved_dict):
                for interface in resolved_dict[self.arguments[attr]].keys():
                    for input in states + exchanges:
                        if interface.providedBy(input):
                            _attributes[attr] = getattr(input, attr)
            else:
                for input in states + exchanges:
                    if hasattr(input, attr):
                        _attributes[attr] = getattr(input, attr)
        _attributes.update(self.resolved_arguments)
        return _attributes

    @checkmate.fix_issue("checkmate/issues/internal_storage_match_R2.rst")
    def match(self, target_copy, reference=None, incoming_list=None):
        """
            >>> import checkmate.runtime._runtime
            >>> import checkmate.runtime.test_plan
            >>> import checkmate.runtime.communication
            >>> import sample_app.application
            >>> import sample_app.component.component_1_states
            >>> import sample_app.component.component_3_states
            >>> t_module = checkmate.runtime.test_plan
            >>> gen = t_module.TestProcedureInitialGenerator(
            ...         sample_app.application.TestData)
            >>> r = checkmate.runtime._runtime.Runtime(
            ...         sample_app.application.TestData,
            ...         checkmate.runtime.communication.Communication)
            >>> run = [run[0] for run in gen][0]
            >>> app = sample_app.application.TestData()
            >>> app.start()
            >>> saved = app.state_list()
            >>> c1 = app.components['C1']
            >>> c3 = app.components['C3']

            >>> c1_states = sample_app.component.component_1_states
            >>> final = [_f for _f in run.final
            ...          if _f.interface == c1_states.IState][0]
            >>> t1 = c1.state_machine.transitions[0]
            >>> c1.simulate(t1) #doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> final.match(app.state_list(), saved) #doctest: +ELLIPSIS
            <sample_app.component.component_1_states.State object at ...

            >>> c3_states = sample_app.component.component_3_states
            >>> final = [_f for _f in run.final
            ...          if _f.interface == c3_states.IAcknowledge][0]
            >>> t3 = c3.state_machine.transitions[0]
            >>> c3.simulate(t3)
            []
            >>> final.match(app.state_list(), saved) #doctest: +ELLIPSIS
            <sample_app.component.component_3_states.Acknowledge ...
        """
        for _target in [_t for _t in target_copy
                        if self.interface.providedBy(_t)]:
            _initial = [None]
            if reference is not None:
                _initial = [_i for _i in reference 
                            if self.interface.providedBy(_i)]
                resolved_arguments = self.resolve(states=_initial,
                                        exchanges=incoming_list)
            else:
                resolved_arguments = self.resolve()

            if _target == self.factory(self.value, instance=_initial[0],
                              default=False, **resolved_arguments):
                return _target
        return None
