import os

import zope.interface

import checkmate.state_machine
import checkmate.parser.doctree

import checkmate._utils


class Component(object):
    def __init__(self, name, matrix='', state_module=None, exchange_module=None):
        self.states = []
        self.name = name
        try:
            visitor_output = checkmate.parser.doctree.call_visitor(matrix, state_module=state_module,
                                                                exchange_module=exchange_module)
            self.state_machine = checkmate.state_machine.StateMachine(visitor_output['states'],
                                                                      visitor_output['transitions'])
        except:
            self.state_machine = checkmate.state_machine.StateMachine()

    def get_transition_by_input(self, exchange):
        """
        >>> import checkmate.test.data_exchange
        >>> import checkmate.test.data_component
        >>> a = checkmate.test.data_component.Abs()
        >>> r_tm = checkmate.test.data_exchange.AbsControlAction('TM()')
        >>> a.get_transition_by_input(r_tm) == a.transitions[0]
        True
        """
        for _t in self.state_machine.transitions:
            if (_t.is_matching_initial(self.states) and
                _t.is_matching_incoming(exchange)):
                return _t
        return None

            
    def start(self):
        for interface, state in self.state_machine.states:
            self.states.append(state[0].factory())

    
def execute(_component, _exchange):
    """
    """
    _transition = _component.get_transition_by_input(_exchange)
    if _transition is None:
        return None
    return _transition.process(_component.states, _exchange)

