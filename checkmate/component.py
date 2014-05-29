import os

import zope.interface

import checkmate._module
import checkmate.state_machine
import checkmate.partition_declarator


class ComponentMeta(type):
    def __new__(cls, name, bases, namespace, **kwds):
        exchange_module = namespace['exchange_module']
        data_structure_module = namespace['data_structure_module']

        state_module = checkmate._module.get_module(namespace['__module__'], name.lower() + '_states')
        namespace['state_module'] = state_module

        path = os.path.dirname(os.path.join(namespace['exchange_definition_file']))
        filename = name.lower() + '.yaml'
        with open(os.sep.join([path, 'component', filename]), 'r') as _file:
            matrix = _file.read()
        try:
            declarator = checkmate.partition_declarator.Declarator(data_structure_module, exchange_module=exchange_module, state_module=state_module, content=matrix)
            declarator_output = declarator.get_output()
            namespace['state_machine'] = checkmate.state_machine.StateMachine(declarator_output['states'], declarator_output['transitions'])
            services = []
            service_interfaces = []
            for _t in declarator_output['transitions']:
                for _i in _t.incoming:
                    if _i.code not in [_service[0] for _service in services]:
                        services.append((_i.code, _i.factory().get_partition_attr()))
                    if _i.interface not in service_interfaces:
                        service_interfaces.append(_i.interface)
            namespace['services'] = services
            namespace['service_interfaces'] = service_interfaces

            result = type.__new__(cls, name, bases, dict(namespace))
            return result
        except Exception as e:
            raise e


class IComponent(zope.interface.Interface):
    """"""

@zope.interface.implementer(IComponent)
class Component(object):
    def __init__(self, name, service_registry):
        self.states = []
        self.name = name
        self.validation_list = []
        self.service_registry = service_registry
        for _tr in self.state_machine.transitions:
            _tr.owner = self.name

    def get_transition_by_input(self, exchange):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start()
        >>> r_tm = c.state_machine.transitions[0].incoming[0].factory()
        >>> c.get_transition_by_input([r_tm]) == c.state_machine.transitions[0]
        True
        """
        for _t in self.state_machine.transitions:
            if (_t.is_matching_initial(self.states) and
                _t.is_matching_incoming(exchange)):
                self._transition_found = True
                return _t
        self._transition_found = False
        return None

            
    def get_transition_by_output(self, exchange):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start()
        >>> for service in c.service_interfaces:
        ...    print(c.service_registry._registry[service])
        ['C1']
        >>> r_tm = c.state_machine.transitions[0].outgoing[0].factory()
        >>> c.get_transition_by_output([r_tm]) == c.state_machine.transitions[0]
        True
        """
        for _t in self.state_machine.transitions:
            if (_t.is_matching_initial(self.states) and
                _t.is_matching_outgoing(exchange)):
                self._transition_found = True
                return _t
        self._transition_found = False
        return None

            
    def start(self):
        for interface, state in self.state_machine.states:
            self.states.append(state.storage[0].factory())
        self.service_registry.register(self, self.service_interfaces)

    def stop(self):
        pass

    def process(self, exchange):
        _transition = self.get_transition_by_input(exchange)
        if _transition is None:
            return []
        output = []
        self.validation_list.append(_transition)
        for _outgoing in _transition.process(self.states, exchange):
            for _e in self.service_registry.server_exchanges(_outgoing, self.name):
                output.append(_e)
        return output

    def simulate(self, _transition):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c2 = a.components['C2']
            >>> c2.start()
            >>> exchange = sample_app.exchanges.AC()
            >>> transition = c2.get_transition_by_output([exchange])

        We can't simulate a transition when no destination for outgoing is registered:
            >>> c2.simulate(transition)
            []

        Registration is done when the destination component is started:
            >>> a.components['C1'].start()
            >>> out = c2.simulate(transition)
            >>> out[0].action == 'AC'
            True
        """
        output = []
        _incoming = _transition.generic_incoming(self.states, self.service_registry)
        for _outgoing in _transition.process(self.states, _incoming):
            for _e in self.service_registry.server_exchanges(_outgoing, self.name):
                output.append(_e)
        return output

    def validate(self, _transition):
        """
            >>> import sample_app.application
            >>> import sample_app.component.component_1
            >>> a = sample_app.application.TestData()
            >>> c1 = a.components['C1']
            >>> c1.start()
            >>> exchange = sample_app.exchanges.AC()
            >>> transition = c1.get_transition_by_input([exchange])
            >>> c1.validate(transition)
            False
            >>> out = c1.process([exchange])
            >>> c1.validate(transition)
            True
            >>> c1.validate(transition)
            False
        """
        result = False
        try:
            self.validation_list.remove(_transition)
            result = True
        except:
            result = False
        return result

    @property
    def transition_not_found(self):
        return not self._transition_found

