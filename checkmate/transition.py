import zope.interface

import checkmate


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
        """Check if the transition incoming list is matching a list of exchange.

        The exchange_list must contain all incoming from the transition to match.

            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C1']
            >>> c.state_machine.transitions[0].name
            'Toggle state tran01'
            >>> i = c.state_machine.transitions[0].incoming[0].factory()
            >>> i.value
            'AC'
            >>> c.state_machine.transitions[0].is_matching_incoming([i])
            True
            >>> c.state_machine.transitions[2].is_matching_incoming([i])
            False

            >>> i = c.state_machine.transitions[1].incoming[0].factory()
        """
        if len(self.incoming) != 0:
            local_copy = list(exchange_list)
            _length = len(local_copy)
            for incoming_exchange in self.incoming:
                local_copy = incoming_exchange.match(local_copy)
                if len(local_copy) == _length:
                    return False
            return len(local_copy) == 0
        else:
            return len(exchange_list) == 0

    def is_matching_outgoing(self, exchange_list):
        """Check if the transition outgoing list is matching a list of exchange.

        The exchange_list can contain only a subset of the transition outgoing
        to match. All item in exchange_list must be matched though.

            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C2']
            >>> i = c.state_machine.transitions[0].outgoing[0].factory()
            >>> i.value
            'AC'
            >>> c.state_machine.transitions[0].is_matching_outgoing([i])
            True
            >>> c.state_machine.transitions[1].is_matching_outgoing([i])
            False
        """
        if len(exchange_list) != 0:
            local_copy = list(exchange_list)
            for outgoing_exchange in self.outgoing:
                local_copy = outgoing_exchange.match(local_copy)
            return len(local_copy) == 0
        else:
            return True

    def is_matching_initial(self, state_list):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C1']
            >>> a.start()
            >>> c.state_machine.transitions[0].is_matching_initial(c.states)
            True
            >>> c.state_machine.transitions[2].is_matching_initial(c.states)
            False

            >>> c3 = a.components['C3']
            >>> c3.states[0].value = 'True'
            >>> t3 = c3.state_machine.transitions[2]
            >>> t3.is_matching_initial(c3.states)
            False
            >>> a.start()
        """
        if len(self.initial) == 0:
            return True
        local_copy = list(state_list)
        for _k in self.initial:
            _length = len(local_copy)
            local_copy = _k.match(local_copy)
            if len(local_copy) == _length:
                return False
        # Do not check len(local_copy) as some state_list are not in self.initial
        return True

    def resolve_arguments(self, _type, data, states, incoming_exchange=[]):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C1']
            >>> c.start()
            >>> t = c.state_machine.transitions[1]
            >>> i = t.incoming[0].factory(kwargs={'R': 1})
            >>> t.resolve_arguments('final', t.final[0], c.states, [i])
            {}
            >>> i = t.incoming[0].factory()
            >>> (i.value, i.R.value)
            ('AP', ['AT1', 'NORM'])
            >>> t.resolve_arguments('final', t.final[0], c.states, [i]) # doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
        """
        return data.resolve(_type, states, incoming_exchange)


    def generic_incoming(self, states, service_registry):
        """ Generate a generic incoming for the provided state

        In case the transition has no incoming, raise AttributeError exception.
        """
        incoming_exchanges = []
        for incoming in self.incoming:
            arguments = self.resolve_arguments('incoming', incoming, states)
            _i = incoming.factory(kwargs=arguments)
            for _e in service_registry.server_exchanges(_i, ''):
                incoming_exchanges.append(_e)
        return incoming_exchanges
            

    @checkmate.report_issue("checkmate/issues/exchange_with_attribute.rst")
    def process(self, states, _incoming):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c = a.components['C1']
            >>> c.start()
            >>> i = c.state_machine.transitions[0].incoming[0].factory()
            >>> c.state_machine.transitions[0].process(c.states, [i]) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> i = c.state_machine.transitions[1].incoming[0].factory()
            >>> o = c.state_machine.transitions[1].process(c.states, [i])
            >>> c.states[1].value # doctest: +ELLIPSIS
            [{'R': ['AT1', 'NORM']}]
        """
        _outgoing_list = []		
        if not self.is_matching_initial(states) or not self.is_matching_incoming(_incoming): 
            return _outgoing_list
        for _state in states:
            for _interface in zope.interface.providedBy(_state):
                for _final in self.final:
                    if _final == None:
                        continue
                    _final_interface = _final.interface
                    if _final_interface == _interface:
                        resolved_arguments = self.resolve_arguments('final', _final, states, _incoming)
                        _final.factory(args=[_state], kwargs=resolved_arguments)
        for outgoing_exchange in self.outgoing:
            resolved_arguments = self.resolve_arguments('outgoing', outgoing_exchange, states, _incoming)
            _outgoing_list.append(outgoing_exchange.factory(kwargs=resolved_arguments))
        return _outgoing_list
