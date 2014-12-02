import zope.interface

import checkmate


class Transition(object):
    """Driving a change of state inside a state machine
    """
    def __init__(self, **argc):
        """"""
        try:
            self.name = argc['tran_name']
        except KeyError:
            self.name = 'unknown'
        finally:
            if self.name == '':
                self.name = 'unknown'
        for item in ['initial', 'incoming', 'final', 'outgoing', 'returned']:
            try:
                setattr(self, item, argc[item])
            except KeyError:
                setattr(self, item, [])

    def matching_list(self, matched_list, partition_list):
        match_list = []
        local_copy = list(partition_list)
        for _k in matched_list:
            match_item = _k.match(local_copy)
            if match_item is not None:
                match_list.append(match_item)
                local_copy.remove(match_item)
        return match_list


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
        match_list = self.matching_list(self.incoming, exchange_list)
        return len(match_list) == len(exchange_list)

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
        match_list = self.matching_list(self.outgoing, exchange_list)
        return len(match_list) == len(exchange_list)

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
        match_list = self.matching_list(self.initial, state_list)
        return len(match_list) == len(self.initial)

    @checkmate.fix_issue('checkmate/issues/generic_incoming_AP_R2.rst')
    def generic_incoming(self, states):
        """ Generate a generic incoming for the provided state

        In case the transition has no incoming, raise AttributeError exception.
        """
        incoming_exchanges = []
        for incoming in self.incoming:
            arguments = incoming.resolve(states)
            incoming_exchanges.append(incoming.factory(**arguments))
        return incoming_exchanges
            

    @checkmate.report_issue("checkmate/issues/exchange_with_attribute.rst")
    @checkmate.fix_issue("checkmate/issues/process_AP_R2.rst")
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
            [{'R': <sample_app.data_structure.ActionRequest object at ...
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
                        resolved_arguments = _final.resolve(states, _incoming)
                        _final.factory(instance=_state, **resolved_arguments)
        for outgoing_exchange in self.outgoing:
            resolved_arguments = outgoing_exchange.resolve(states, _incoming)
            _outgoing_list.append(outgoing_exchange.factory(**resolved_arguments))
        return _outgoing_list
