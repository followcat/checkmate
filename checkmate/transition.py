import sys

import zope.interface

import checkmate.state
import checkmate._utils

import checkmate._storage


class Transition(object):
    """Driving a change of state inside a state machine
    """
    def __init__(self, **argc):
        self.initial = []
        self.incoming = None
        self.final = []
        self.outgoing = []
        for item in ['initial', 'incoming', 'final', 'outgoing']:
            _attribute = getattr(self, item)
            if (item in argc) == False:
                continue
            for _interface, _name in argc[item]:
                _o = checkmate._utils.get_class_implementing(_interface)
                _arguments, _kw_arguments = checkmate._utils.method_arguments(_name)

                if item in ['initial', 'final']:
                    getattr(self, item).append(checkmate._storage.store_state(_interface, _name))
                elif item == 'incoming':
                    self.incoming = checkmate._storage.store_exchange(_interface, _name)
                elif item == 'outgoing':
                    self.outgoing.append(checkmate._storage.store_exchange(_interface, _name))


    def is_matching_incoming(self, exchange):
        """
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> c = a.components['C1']
            >>> i = c.state_machine.transitions[0].incoming.factory()
            >>> c.state_machine.transitions[0].is_matching_incoming(i)
            True
            >>> c.state_machine.transitions[3].is_matching_incoming(i)
            False
        """
        if self.incoming is not None:
            _interface = self.incoming.interface
            if _interface.providedBy(exchange):
                obj = self.incoming.factory()
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

    def resolve_arguments(self, type, data, states, incoming=None):
        """
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> c = a.components['C1']
            >>> c.start()
            >>> t = c.state_machine.transitions[1]
            >>> i = t.incoming.factory()
            >>> t.resolve_arguments('final', t.final[0], c.states, i)
            {'R': None}
            >>> i = t.incoming.factory(kwargs={'R': 1})
            >>> t.resolve_arguments('final', t.final[0], c.states, i)
            {'R': 1}
        """
        resolved_arguments = {}
        entry = getattr(self, type)
        if type == 'incoming':
            arguments = list(entry.kw_arguments.keys())
        else:
            arguments = list(entry[entry.index(data)].kw_arguments.keys())
        for arg in arguments:
            found = False
            resolved_value = None
            if type in ['final', 'incoming']:
                for item in self.initial:
                    if arg == item.code:
                        for _state in states:
                            if item.interface.providedBy(_state):
                                resolved_value = _state.value
                                found = True
                                break
                    if found:
                        break
            if ((not found) and self.incoming is not None):
                if type in ['final', 'outgoing']:
                    if arg in list(self.incoming.kw_arguments.keys()):
                        if arg in iter(incoming.parameters):
                            resolved_value = incoming.parameters[arg]
                            found = True
            if not found:
                if type in ['outgoing']:
                    for item in self.final:
                        if arg == item.code:
                            for _state in states:
                                if item.interface.providedBy(_state):
                                    resolved_value = _state.value
                                    found = True
                                    break
                        if found:
                            break
            if found:
                resolved_arguments[arg] = resolved_value
        return resolved_arguments


    def generic_incoming(self, states):
        """ Generate a generic incoming for the provided state

        In case the transition has no incoming, raise AttributeError exception.
        """
        arguments = self.resolve_arguments('incoming', self.incoming, states)
        return self.incoming.factory(kwargs=arguments)
            

    def process(self, states, _incoming):
        """
            >>> import checkmate.test_data
            >>> a = checkmate.test_data.App()
            >>> c = a.components['C1']
            >>> c.start()
            >>> i = c.state_machine.transitions[0].incoming.factory()
            >>> c.state_machine.transitions[0].process(c.states, i) # doctest: +ELLIPSIS
            [<sample_app.exchanges.Reaction object at ...
            >>> i = c.state_machine.transitions[1].incoming.factory()
            >>> o = c.state_machine.transitions[1].process(c.states, i)
            >>> c.states[1].value
            [{'R': None}]
            >>> i = c.state_machine.transitions[1].incoming.factory(kwargs={'R': 1})
            >>> o = c.state_machine.transitions[1].process(c.states, i)
            >>> c.states[1].value
            [{'R': None}, {'R': 1}]
        """
        def member_wrapper(cls, obj, args=[], kwargs={}):
            return cls(obj, *args, **kwargs)

        for _state in states:
            for _interface in zope.interface.providedBy(_state):
                for _final in self.final:
                    if _final == None:
                        continue
                    _final_interface = _final.interface
                    if _final_interface == _interface:
                        if len(_final.kw_arguments) == 0:
                            _final.factory(args=[_state])
                        else:
                            resolved_arguments = self.resolve_arguments('final', _final, states, _incoming)
                            member_wrapper(_final.function, _state, kwargs=resolved_arguments)
        _outgoing_list = []

        for outgoing_exchange in self.outgoing:
            resolved_arguments = self.resolve_arguments('outgoing', outgoing_exchange, states, _incoming)
            _outgoing_list.append(outgoing_exchange.factory(kwargs=resolved_arguments))
        return _outgoing_list

