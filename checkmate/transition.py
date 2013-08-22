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


    def is_matching_incoming(self, exchange):
        """
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> c = a.components['C1']
            >>> c.state_machine.transitions[0].name
            'Toggle state tran01'
            >>> i = c.state_machine.transitions[0].incoming[0].factory()
            >>> i.action
            'AC'
            >>> c.state_machine.transitions[0].is_matching_incoming(i)
            True
            >>> c.state_machine.transitions[3].is_matching_incoming(i)
            False

            >>> i = c.state_machine.transitions[1].incoming[0].factory()
        """
        if len(self.incoming) != 0:
            for incoming_exchange in self.incoming:
                _interface = incoming_exchange.interface
                if _interface.providedBy(exchange):
                    obj = incoming_exchange.factory()
                    if exchange == obj:
                        return True
        return False

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
        for _k in self.initial:
            _interface = _k.interface
            for _s in state_list:
                if _interface.providedBy(_s):
                    obj = _k.factory()
                    if _s == obj:
                        return True
        return False

    def resolve_arguments(self, _type, data, states, incoming_exchange=None):
        """
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> c = a.components['C1']
            >>> c.start()
            >>> t = c.state_machine.transitions[1]
            >>> i = t.incoming[0].factory(kwargs={'R': 1})
            >>> t.resolve_arguments('final', t.final[0], c.states, i)
            {'R': 1}
            >>> i = t.incoming[0].factory()
            >>> (i.action, i.R.P.value)
            ('AP', 'NORM')
            >>> t.resolve_arguments('final', t.final[0], c.states, i) # doctest: +ELLIPSIS
            {'R': <sample_app.data_structure.ActionRequest object at ...
        """
        resolved_arguments = {}
        entry = getattr(self, _type)
        arguments = list(entry[entry.index(data)].arguments.attribute_values.keys())
        for arg in arguments:
            try:
                resolved_arguments.update(data.resolve(arg, states=states, exchange=incoming_exchange))
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
            >>> c.state_machine.transitions[0].process(c.states, i) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> i = c.state_machine.transitions[1].incoming[0].factory()
            >>> o = c.state_machine.transitions[1].process(c.states, i)
            >>> c.states[1].value # doctest: +ELLIPSIS
            [{'R': <sample_app.data_structure.ActionRequest object at ...
            >>> i = c.state_machine.transitions[1].incoming[0].factory(kwargs={'R': 1})
            >>> o = c.state_machine.transitions[1].process(c.states, i)
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

