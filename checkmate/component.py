import os

import zope.interface

import checkmate.state_machine
import checkmate.partition_declarator
import checkmate.service_registry


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
            declarator = checkmate.partition_declarator.Declarator(data_structure_module, state_module=state_module, exchange_module=exchange_module, content=matrix)
            declarator_output = declarator.get_output()
            namespace['state_machine'] = checkmate.state_machine.StateMachine(declarator_output['states'],
                                                                      declarator_output['transitions'])
            namespace['services'] = declarator_output['services']
            namespace['outgoings'] = declarator_output['outgoings']
            result = type.__new__(cls, name, bases, dict(namespace))
            return result
        except Exception as e:
            raise e


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
        >>> r_tm = c.state_machine.transitions[0].incoming[0].factory()
        >>> c.get_transition_by_input([r_tm]) == c.state_machine.transitions[0]
        True
        """
        for _t in self.state_machine.transitions:
            if (_t.is_matching_initial(self.states) and
                _t.is_matching_incoming(exchange)):
                return _t
        return None

            
    def get_transition_by_output(self, exchange):
        """
        >>> import checkmate.test_data
        >>> a = checkmate.test_data.App()
        >>> c = a.components['C1']
        >>> c.start()
        >>> r = checkmate.service_registry.global_registry
        >>> for service in c.services:
        ...    print(r._registry[service])
        ['C1']
        >>> r_tm = c.state_machine.transitions[0].outgoing[0].factory()
        >>> c.get_transition_by_output([r_tm]) == c.state_machine.transitions[0]
        True
        """
        for _t in self.state_machine.transitions:
            if (_t.is_matching_initial(self.states) and
                _t.is_matching_outgoing(exchange)):
                return _t
        return None

            
    def start(self):
        for interface, state in self.state_machine.states:
            self.states.append(state.storage[0].factory())
        checkmate.service_registry.global_registry.register(self, self.services)

    def stop(self):
        pass

    def process(self, exchange):
        _transition = self.get_transition_by_input(exchange)
        if _transition is None:
            return []
        output = []
        for _outgoing in _transition.process(self.states, exchange):
            for _e in checkmate.service_registry.global_registry.server_exchanges(_outgoing, self.name):
                output.append(_e)
        return output

    def simulate(self, exchange):
        """
            >>> import sample_app.application
            >>> import sample_app.component_2.component
            >>> c2 = sample_app.component_2.component.Component_2('C2')
            >>> c2.start()
            >>> out = c2.simulate(sample_app.exchanges.AC())
            >>> out[0].action == 'AC'
            True
        """
        _transition = self.get_transition_by_output([exchange])
        if _transition is None:
            return []
        output = []
        _incoming = _transition.generic_incoming(self.states)
        for _outgoing in _transition.process(self.states, _incoming):
            for _e in checkmate.service_registry.global_registry.server_exchanges(_outgoing, self.name):
                output.append(_e)
        return output

