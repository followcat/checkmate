import zope.interface


class Transition(object):
    """Driving a change of state inside a state machine
    """
    def __init__(self, **argc):
        self.initial = []
        self.incoming = []
        self.final = []
        self.outgoing = []
        try:
            self.name = argc['tran_name']
        except KeyError:
            self.name = 'unknown'
        finally:
            if self.name == '':
                self.name = 'unknown'
        for item in ['initial', 'incoming', 'final', 'outgoing']:
            if (item in argc) == False:
                continue
            setattr(self, item, argc[item])


    def is_matching_incoming(self, exchange_list):
        """
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> c = a.components['C1']
            >>> c.state_machine.transitions[0].name
            'Toggle state tran01'
            >>> i = c.state_machine.transitions[0].incoming[0].factory()
            >>> i.action
            'AC'
            >>> c.state_machine.transitions[0].is_matching_incoming([i])
            True
            >>> c.state_machine.transitions[3].is_matching_incoming([i])
            False

            >>> i = c.state_machine.transitions[1].incoming[0].factory()
        """
        if len(self.incoming) != 0:
            local_copy = list(exchange_list)
            for incoming_exchange in self.incoming:
                found = False
                _interface = incoming_exchange.interface
                for _exchange in [_e for _e in local_copy if _interface.providedBy(_e)]:
                    obj = incoming_exchange.factory()
                    if _exchange == obj:
                        local_copy.remove(_exchange)
                        found = True
                        break
                if not found:
                    return False
            return len(local_copy) == 0
        else:
            return len(exchange_list) == 0

    def is_matching_initial(self, state_list):
        """
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> c = a.components['C1']
            >>> c.start()
            >>> c.state_machine.transitions[0].is_matching_initial(c.states)
            True
            >>> c.state_machine.transitions[3].is_matching_initial(c.states)
            False
        """
        if len(self.initial) == 0:
            return True
        local_copy = list(state_list)
        for _k in self.initial:
            found = False
            _interface = _k.interface
            for _state in [_s for _s in local_copy if _interface.providedBy(_s)]:
                obj = _k.factory()
                if _state == obj:
                    found = True
                    local_copy.remove(_state)
                    break
            if not found:
                return False
        # Do not check len(local_copy) as some state_list are not in self.initial
        return True

    def resolve_arguments(self, _type, data, states, incoming_exchange=[]):
        """
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> c = a.components['C1']
            >>> c.start()
            >>> t = c.state_machine.transitions[1]
            >>> i = t.incoming[0].factory(kwargs={'R': 1})
            >>> t.resolve_arguments('final', t.final[0], c.states, [i])
            {'R': 1}
            >>> i = t.incoming[0].factory()
            >>> (i.action, i.R.P.value)
            ('AP', 'NORM')
            >>> t.resolve_arguments('final', t.final[0], c.states, [i]) # doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
        """
        resolved_arguments = {}
        entry = getattr(self, _type)
        arguments = list(entry[entry.index(data)].arguments.attribute_values.keys())
        for arg in arguments:
            try:
                resolved_arguments.update(data.resolve(arg, states=states, exchanges=incoming_exchange))
            except AttributeError:
                continue
        return resolved_arguments


    def generic_incoming(self, states):
        """ Generate a generic incoming for the provided state

        In case the transition has no incoming, raise AttributeError exception.
        """
        incoming_exchanges = []
        for incoming in self.incoming:
            arguments = self.resolve_arguments('incoming', incoming, states)
            incoming_exchanges.append(incoming.factory(kwargs=arguments))
        return incoming_exchanges
            

    def process(self, states, _incoming):
        """
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> c = a.components['C1']
            >>> c.start()
            >>> i = c.state_machine.transitions[0].incoming[0].factory()
            >>> c.state_machine.transitions[0].process(c.states, [i]) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> i = c.state_machine.transitions[1].incoming[0].factory()
            >>> o = c.state_machine.transitions[1].process(c.states, [i])
            >>> c.states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object at ...
            >>> i = c.state_machine.transitions[1].incoming[0].factory(kwargs={'R': 1})
            >>> o = c.state_machine.transitions[1].process(c.states, [i])
            >>> c.states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object at ...
        """
        for _state in states:
            for _interface in zope.interface.providedBy(_state):
                for _final in self.final:
                    if _final == None:
                        continue
                    _final_interface = _final.interface
                    if _final_interface == _interface:
                        resolved_arguments = self.resolve_arguments('final', _final, states, _incoming)
                        _final.factory(args=[_state], kwargs=resolved_arguments)
        _outgoing_list = []

        for outgoing_exchange in self.outgoing:
            resolved_arguments = self.resolve_arguments('outgoing', outgoing_exchange, states, _incoming)
            _outgoing_list.append(outgoing_exchange.factory(kwargs=resolved_arguments))
        return _outgoing_list

