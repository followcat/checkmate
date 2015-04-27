# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import checkmate
import checkmate._storage


def make_transition(items, exchanges, state_modules):
    module_dict = {'states': state_modules,
                   'exchanges': exchanges}
    ts = TransitionStorage(items, module_dict)
    return ts.factory()


def new_transition(items, exchange_module, state_module):
    """
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
    ...     'signature': 'TestActionRequest',
    ...     'codes_list': ['TestActionRequestNORM'],
    ...     'values_list': ['NORM'],
    ...     }
    >>> de.new_partition(items)
    >>> items = {
    ...     'partition_type': 'states',
    ...     'signature': 'TestState',
    ...     'codes_list': ['TestStateTrue()', 'TestStateFalse()'],
    ...     'values_list': [True, False],
    ...     }
    >>> de.new_partition(items)
    >>> items = {
    ...     'partition_type': 'exchanges',
    ...     'signature': 'TestReturn()',
    ...     'codes_list': ['DA()'],
    ...     'values_list': ['DA']
    ...     }
    >>> de.new_partition(items)
    >>> item = {'name': 'Toggle TestState tran01',
    ...         'initial': [{'TestState': 'TestStateTrue'}],
    ...         'outgoing': [{'TestReturn': 'DA()'}],
    ...         'incoming': [{'TestAction': 'AP(R)'}],
    ...         'final': [{'TestState': 'TestStateFalse'}]}
    >>> checkmate.tymata.transition.new_transition(item,
    ...     exchange_module,
    ...     state_module) # doctest: +ELLIPSIS
    <checkmate.tymata.transition.Transition object at ...
    """
    return checkmate.tymata.transition.make_transition(
        items, [exchange_module], [state_module])


class TransitionStorage(object):
    def __init__(self, items, module_dict):
        """"""
        super().__init__()
        self.name = ''
        self.initializing = False
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
            elif _k == 'initializing' and _v == True:
                self.initializing = True
                continue
            elif _k == 'name':
                self.name = _v
                continue
            for each_item in _v:
                for _name, _data in each_item.items():
                    code = checkmate._exec_tools.get_method_basename(_data)
                    define_class = checkmate._storage.name_to_class(
                        _name, module_dict[module_type])
                    arguments = checkmate._exec_tools.get_signature_arguments(
                                    _data, define_class)
                    generate_storage = checkmate._storage.InternalStorage(
                        define_class, _data, None, arguments=arguments)
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
        return checkmate.tymata.transition.Transition(
                                               tran_name=self.name,
                                               initializing=self.initializing,
                                               initial=self.initial,
                                               incoming=self.incoming,
                                               final=self.final,
                                               outgoing=self.outgoing,
                                               returned=self.returned)


class Block(object):
    """"""


class Transition(Block):
    """Driving a change of state inside a state machine
    """
    def __init__(self, **argc):
        """"""
        self.owner = ''
        self.initializing = argc['initializing']
        try:
            self.name = argc['tran_name']
        except KeyError:
            self.name = 'unknown'
        finally:
            if self.name == '':
                self.name = 'unknown'
        self.resolve_dict = {}
        for item in ['initial', 'incoming', 'final', 'outgoing', 'returned']:
            try:
                setattr(self, item, argc[item])
            except KeyError:
                setattr(self, item, [])
        for _s in argc['initial'] + argc['incoming']:
            for key, value in _s.arguments.items():
                if type(value) == tuple:
                    continue
                self.resolve_dict[value] = (_s.partition_class, key)

    def matching_list(self, matched_list, partition_list):
        match_list = []
        local_copy = list(partition_list)
        for _k in matched_list:
            match_item = _k.match(local_copy)
            if match_item is not None:
                match_list.append(match_item)
                local_copy.remove(match_item)
        return match_list

    def is_matching_incoming(self, exchange_list, state_list):
        """Check if the transition incoming list is matching a list of
        exchange.

        The exchange_list must contain all incoming from the transition
        to match.

            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C1']
            >>> c.engine.blocks[0].name
            'Toggle state tran01'
            >>> c.engine.blocks[0].initializing
            False
            >>> i = c.engine.blocks[0].incoming[0].factory()
            >>> i.value
            'AC'
            >>> s = c.states
            >>> c.engine.blocks[0].is_matching_incoming([i], s)
            True
            >>> c.engine.blocks[2].is_matching_incoming([i], s)
            False

            >>> i = c.engine.blocks[1].incoming[0].factory()
        """
        keys = {}
        if len(exchange_list) > 0:
            for key, value in self.resolve_dict.items():
                partition_class, attr = value
                if hasattr(exchange_list[0], attr):
                    if attr not in keys:
                        keys[attr] = []
                    keys[attr].append(key)
        for key, attr_list in keys.items():
            if key not in attr_list and len(set(attr_list)) > 1:
                compare_list = []
                for attr in attr_list:
                    partition_class = self.resolve_dict[attr][0]
                    for input in state_list + exchange_list:
                        if isinstance(input, partition_class):
                            compare_list.append(getattr(input, key))
                if len(compare_list) > 1 and compare_list[0] == compare_list[1]:
                    return False
        match_list = self.matching_list(self.incoming, exchange_list)
        return len(match_list) == len(exchange_list)

    def is_matching_outgoing(self, exchange_list):
        """Check if the transition outgoing list is matching a list of
        exchange.

        The exchange_list can contain only a subset of the transition
        outgoing to match. All item in exchange_list must be matched
        though.

            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C2']
            >>> i = c.engine.blocks[0].outgoing[0].factory()
            >>> i.value
            'AC'
            >>> c.engine.blocks[0].is_matching_outgoing([i])
            True
            >>> c.engine.blocks[1].is_matching_outgoing([i])
            False
        """
        match_list = self.matching_list(self.outgoing, exchange_list)
        return len(match_list) == len(exchange_list)

    def is_matching_initial(self, state_list):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C1']
            >>> a.start()
            >>> engine = c.engine
            >>> engine.blocks[0].is_matching_initial(c.states)
            True
            >>> engine.blocks[2].is_matching_initial(c.states)
            False

            >>> c3 = a.components['C3']
            >>> c3.states[0].value = True
            >>> t3 = c3.engine.blocks[2]
            >>> t3.is_matching_initial(c3.states)
            False
            >>> a.start()
        """
        match_list = self.matching_list(self.initial, state_list)
        return len(match_list) == len(self.initial)

    @checkmate.fix_issue('checkmate/issues/generic_incoming_AP_R2.rst')
    def generic_incoming(self, states, *args, default=True):
        """ Generate a generic incoming for the provided state

        In case the transition has no incoming, raise AttributeError
        exception.
        """
        incoming_exchanges = []
        for incoming in self.incoming:
            arguments = incoming.resolve(states)
            incoming_exchanges.append(
                incoming.factory(incoming.value, default=False, **arguments))
        return incoming_exchanges

    @checkmate.report_issue("checkmate/issues/exchange_with_attribute.rst")
    @checkmate.fix_issue("checkmate/issues/process_AP_R2.rst")
    def process(self, states, _incoming, *args, default=True):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C1']
            >>> c.start()
            >>> ts = c.engine.blocks
            >>> i = ts[0].incoming[0].factory()
            >>> ts[0].process(c.states, [i]) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> i = ts[1].incoming[0].factory()
            >>> o = ts[1].process(c.states, [i])
            >>> c.states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object ...
        """
        _outgoing_list = []
        if not self.is_matching_initial(states) or \
           not self.is_matching_incoming(_incoming, states):
            return _outgoing_list
        for _state in states:
            for _final in self.final:
                if isinstance(_state, _final.partition_class):
                    resolved_arguments = _final.resolve(states, _incoming,
                                                        self.resolve_dict)
                    _final.factory(instance=_state, default=default,
                        **resolved_arguments)
        for outgoing_exchange in self.outgoing:
            resolved_arguments = outgoing_exchange.resolve(states, _incoming,
                                                           self.resolve_dict)
            _outgoing_list.append(
                outgoing_exchange.factory(outgoing_exchange.value,
                    default=default, **resolved_arguments))
        return _outgoing_list
