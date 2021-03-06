# This code is part of the checkmate project.
# Copyright (C) 2013-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import checkmate._module
import checkmate._exec_tools
import checkmate.tymata.transition


class PartitionStorage(object):
    def __init__(self, partition_class, code_arguments,
                 full_description=None):
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
            >>> data = checkmate._storage.PartitionStorage(
            ...             c1_module.AnotherState,
            ...             {'AnotherState1()': {'value': 'None'}})
            >>> state = data.storage[0].factory()
            >>> state.value
            >>> data = checkmate._storage.PartitionStorage(
            ...         sample_app.exchanges.Action,
            ...         {'AP(R)': {'value': 'AP'}})
            >>> ex = data.storage[0].factory(R='HIGH')
            >>> (ex.value, ex.R.value)
            ('AP', 'HIGH')
        """
        self.type = type
        self.full_description = full_description
        self.partition_class = partition_class
        self.storage = []
        for code, arguments in code_arguments.items():
            try:
                code_description = self.full_description[code]
            except:
                code_description = (None, None)
            try:
                value = arguments.pop('value')
            except KeyError:
                value = None
            _storage = InternalStorage(self.partition_class,
                                       code, code_description,
                                       value=value, arguments=arguments)
            self.storage.append(_storage)

    def get_description(self, item):
        """ Return description corresponding to item """
        for stored_item in list(self.storage):
            if item == stored_item.factory():
                return stored_item.description
        return (None, None)


class InternalStorage(object):
    """Support local storage of data (status or data_structure)
    information in transition"""
    def __init__(self, partition_class, code, description,
                 value=None, arguments={}):
        """
            >>> import sample_app.application
            >>> import sample_app.exchanges
            >>> import checkmate._storage
            >>> st = checkmate._storage.InternalStorage(
            ...         sample_app.exchanges.Action,
            ...         "AP(R)",  None, value="AP(R)")
            >>> [st.factory().R.C.value, st.factory().R.P.value]
            ['AT1', 'NORM']
        """
        self.origin_code = code
        self.code = checkmate._exec_tools.get_method_basename(code)
        self.description = description
        self.partition_class = partition_class
        self.function = self.partition_class

        self.arguments = dict(arguments)
        self.resolved_arguments = self.function.method_arguments(self.arguments)
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
            ...         sample_app.exchanges.Action,
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
            >>> t = c.engine.blocks[2]
            >>> i = t.incoming[0].factory(); i.value
            'PP'
            >>> t.final[1].function # doctest: +ELLIPSIS
            <function State.pop at ...
            >>> arguments = t.final[1].resolve(exchanges=[i],
            ...                 resolved_dict=t.resolve_dict)
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
        if instance is not None and isinstance(instance, self.partition_class):
            try:
                value = self.value
            except IndexError:
                value = None
            self.function(instance, value, **kwargs)
            return instance
        else:
            return self.function(*args, **kwargs)

    @checkmate.fix_issue("checkmate/issues/transition_resolve_arguments.rst")
    def resolve(self, states=None, exchanges=None, resolved_dict=None):
        """
            >>> import sample_app.application
            >>> import sample_app.exchanges
            >>> import checkmate.tymata.transition
            >>> a = sample_app.application.TestData()
            >>> t = a.components['C1'].engine.blocks[1]
            >>> inc = t.incoming[0].factory()
            >>> states = [t.initial[0].factory()]
            >>> t.final[0].resolve(states, resolved_dict=t.resolve_dict)
            {}
            >>> t.final[0].resolve(exchanges=[inc],
            ...     resolved_dict=t.resolve_dict) # doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
            >>> inc = t.incoming[0].factory(R=['AT2', 'HIGH'])
            >>> inc.R.value
            ['AT2', 'HIGH']
            >>> t.final[0].resolve(exchanges=[inc],
            ...     resolved_dict=t.resolve_dict) # doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
            >>> inc = t.incoming[0].factory(R=1)
            >>> (inc.value, inc.R.value)  # doctest: +ELLIPSIS
            ('AP', 1)
            >>> t.final[0].resolve(exchanges=[inc],
            ...     resolved_dict=t.resolve_dict) # doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
            >>> item = {'name': 'Toggle TestState tran01',
            ...         'outgoing': [{'Action': 'AP(R2)'}],
            ...         'incoming': [{'AnotherReaction': 'ARE()'}]}
            >>> t = checkmate.tymata.transition.make_transition(
            ...         item, [sample_app.exchanges],
            ...         [sample_app.component.component_1_states])
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
        if resolved_dict is None:
            resolved_dict = {}
        _attributes = {}
        for attr, data_cls in self.partition_class._construct_values.items():
            if (attr in self.arguments and
                    type(self.arguments[attr]) != tuple and
                    self.arguments[attr] in resolved_dict):
                partition_class, attr = resolved_dict[self.arguments[attr]]
                for input in states + exchanges:
                    if (hasattr(input, attr) and
                            isinstance(input, partition_class)):
                        data = getattr(input, attr)
                        if isinstance(data, data_cls):
                            _attributes[attr] = data
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
            ...          if _f.partition_class == c1_states.State][0]
            >>> t1 = c1.engine.blocks[0]
            >>> c1.simulate(t1) #doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> final.match(app.state_list(), saved) #doctest: +ELLIPSIS
            <sample_app.component.component_1_states.State object at ...

            >>> c3_states = sample_app.component.component_3_states
            >>> final = [_f for _f in run.final
            ...          if _f.partition_class == c3_states.Acknowledge][0]
            >>> t3 = c3.engine.blocks[0]
            >>> c3.simulate(t3)
            []
            >>> final.match(app.state_list(), saved) #doctest: +ELLIPSIS
            <sample_app.component.component_3_states.Acknowledge ...
        """
        for _target in [_t for _t in target_copy
                        if isinstance(_t, self.partition_class)]:
            _initial = [None]
            if reference is not None:
                _initial = [_i for _i in reference 
                            if isinstance(_i, self.partition_class)]
                resolved_arguments = self.resolve(states=_initial,
                                        exchanges=incoming_list)
            else:
                resolved_arguments = self.resolve()

            if _target == self.factory(self.value, instance=_initial[0],
                              default=False, **resolved_arguments):
                return _target
        return None

    def __key(self):
        return (self.partition_class, self.value)

    def __eq__(self, other):
        """
            >>> import sample_app.application
            >>> state = sample_app.component.component_1_states.State
            >>> (state.partition_storage.storage[0] ==
            ... sample_app.component.component_1.Component_1.
            ... instance_engines['C1'].blocks[0].initial[0])
            True
        """
        assert type(other) == InternalStorage
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())
