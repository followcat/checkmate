import os

import zope.interface

import checkmate._module
import checkmate._validation
import checkmate.state_machine
import checkmate.partition_declarator


class ComponentMeta(type):
    def __new__(cls, name, bases, namespace, **kwds):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c1 = a.components['C1']
        >>> c2 = a.components['C2']
        >>> c3 = a.components['C3']
        >>> c1.exchange_module #doctest: +ELLIPSIS
        <module 'sample_app.exchanges' from ...
        >>> c1.state_module #doctest: +ELLIPSIS
        <module 'sample_app.component.component_1_states' from ...
        >>> c1.is_publish, c2.is_publish, c3.is_publish
        (True, False, False)
        >>> c1.publish_exchange, c2.publish_exchange, c3.publish_exchange
        (['PA'], [], [])
        >>> c1.subscribe_exchange, c2.subscribe_exchange, c3.subscribe_exchange
        ([], ['PA'], ['PA'])
        """
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
            outgoings = []
            namespace['is_publish'] = False
            namespace['subscribe_exchange'] = []
            namespace['publish_exchange'] = []
            for _t in declarator_output['transitions']:
                for _i in _t.incoming:
                    if _i.code not in [_service[0] for _service in services]:
                        services.append((_i.code, _i.factory().get_partition_attr()))
                    if _i.interface not in service_interfaces:
                        service_interfaces.append(_i.interface)
                    if _i.factory().broadcast:
                        namespace['subscribe_exchange'].append(_i.code)
                for _o in _t.outgoing:
                    if _o.code not in outgoings:
                        outgoings.append(_o.code)
                    if _o.factory().broadcast:
                        namespace['publish_exchange'].append(_o.code)
                        namespace['is_publish'] = True
            namespace['services'] = services
            namespace['service_interfaces'] = service_interfaces
            namespace['outgoings'] = outgoings

            result = type.__new__(cls, name, bases, dict(namespace))
            return result
        except Exception as e:
            raise e


class IComponent(zope.interface.Interface):
    """"""

@zope.interface.implementer(IComponent)
class Component(object):
    def __init__(self, name, service_registry):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> a.start()
        >>> c = a.components['C1']
        >>> c.name
        'C1'
        >>> len(c.states) 
        2
        """
        self.states = []
        self.name = name
        self.validation_list = checkmate._validation.List(self.state_machine.transitions)
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
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.states
        []
        >>> c.start()
        >>> c.states #doctest: +ELLIPSIS
        [<sample_app.component.component_1_states.State object at ...
        """
        for interface, state in self.state_machine.states:
            self.states.append(state.storage[0].factory())
        self.service_registry.register(self, self.service_interfaces)

    def reset(self):
        self.validation_list.clear()

    def stop(self):
        pass

    def process(self, exchange):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start()
        >>> transition=c.state_machine.transitions[0]
        >>> transition.is_matching_initial(c.states)
        True
        >>> output = transition.process(c.states, [sample_app.exchanges.AC()])
        >>> output[0].value
        'RE'
        >>> output[1].value
        'ARE'
        >>> transition.is_matching_initial(c.states)
        False
        """
        _transition = self.get_transition_by_input(exchange)
        if _transition is None:
            return []
        output = []
        self.validation_list.record(_transition, exchange)
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
            >>> out[0].value == 'AC'
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
        return self.validation_list.check(_transition)

    def get_all_validated_incoming(self):
        return self.validation_list.all_items()

    @property
    def transition_not_found(self):
        return not self._transition_found

