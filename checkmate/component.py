import os

import zope.interface

import checkmate.state_machine
import checkmate.parser.dtvisitor
import checkmate.partition_declarator


class ComponentMeta(type):
    def __new__(cls, name, bases, namespace, **kwds):
        state_module = namespace['state_module']
        data_structure_module = namespace['data_structure_module']
        exchange_module = namespace['exchange_module']

        path = os.path.dirname(state_module.__file__)
        filename = 'state_machine.rst'
        _file = open(os.sep.join([path, filename]), 'r')
        matrix = _file.read()
        _file.close()
        try:
            declarator = checkmate.partition_declarator.Declarator(data_structure_module, state_module=state_module, exchange_module=exchange_module)
            visitor_output = checkmate.parser.dtvisitor.call_visitor(matrix, declarator)
            namespace['state_machine'] = checkmate.state_machine.StateMachine(visitor_output['states'],
                                                                      visitor_output['transitions'])
        except:
            namespace['state_machine'] = checkmate.state_machine.StateMachine()
        finally:
            result = type.__new__(cls, name, bases, dict(namespace))
            return result


class IComponent(zope.interface.Interface):
    """"""

@zope.interface.implementer(IComponent)
class Component(object):
    def __init__(self, name):
        self.states = []
        self.name = name

    def get_transition_by_input(self, exchange):
        """
        >>> import checkmate.test_data
        >>> a = checkmate.test_data.App()
        >>> c = a.components['C1']
        >>> c.start()
        >>> r_tm = c.state_machine.transitions[0].incoming.factory()
        >>> c.get_transition_by_input(r_tm) == c.state_machine.transitions[0]
        True
        """
        for _t in self.state_machine.transitions:
            if (_t.is_matching_initial(self.states) and
                _t.is_matching_incoming(exchange)):
                return _t
        return None

            
    def start(self):
        for interface, state in self.state_machine.states:
            self.states.append(state.storage[0].factory())

    
def execute(_component, _exchange):
    """
    """
    _transition = _component.get_transition_by_input(_exchange)
    if _transition is None:
        return None
    return _transition.process(_component.states, _exchange)

