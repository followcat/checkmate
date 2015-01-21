import os

import zope.interface

import checkmate._module
import checkmate._validation
import checkmate.exception
import checkmate.interfaces
import checkmate.state_machine
import checkmate.parser.yaml_visitor
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
        >>> c1.publish_exchange, c2.publish_exchange, c3.publish_exchange
        (['PA'], [], [])
        >>> c1.subscribe_exchange, c2.subscribe_exchange, c3.subscribe_exchange
        ([], ['PA'], ['PA'])
        """
        exchange_module = namespace['exchange_module']
        data_structure_module = namespace['data_structure_module']

        state_module = checkmate._module.get_module(namespace['__module__'], name.lower() + '_states')
        namespace['state_module'] = state_module

        paths = namespace['component_definition']
        if type(paths) != list:
            paths = [paths]
        filename = name.lower() + '.yaml'
        define_data = ''
        for path in paths:
            if not os.path.isdir(path):
                continue
            with open(os.sep.join([path, filename]), 'r') as _file:
                define_data += _file.read()
        data_source = checkmate.parser.yaml_visitor.call_visitor(define_data)
        try:
            declarator = checkmate.partition_declarator.Declarator(data_structure_module, exchange_module=exchange_module, state_module=state_module)
            declarator.new_definitions(data_source)
            declarator_output = declarator.get_output()
            namespace['state_machine'] = checkmate.state_machine.StateMachine(declarator_output['states'], declarator_output['transitions'])
            services = []
            service_interfaces = []
            outgoings = []
            namespace['subscribe_exchange'] = []
            namespace['publish_exchange'] = []
            for _t in declarator_output['transitions']:
                for _i in _t.incoming:
                    if _i.code not in [_service[0] for _service in services]:
                        services.append((_i.code, _i.factory()))
                    if _i.interface not in service_interfaces:
                        service_interfaces.append(_i.interface)
                    if _i.factory().broadcast:
                        namespace['subscribe_exchange'].append(_i.code)
                for _o in _t.outgoing:
                    if _o.code not in outgoings:
                        outgoings.append(_o.code)
                    if _o.factory().broadcast:
                        namespace['publish_exchange'].append(_o.code)
            namespace['services'] = services
            namespace['service_interfaces'] = service_interfaces
            namespace['outgoings'] = outgoings

            result = type.__new__(cls, name, bases, dict(namespace))
            return result
        except Exception as e:
            raise e


@zope.interface.implementer(checkmate.interfaces.IComponent)
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
        self.pending_incoming = []
        self.pending_outgoing = []
        self.default_state_value = True
        self.expected_return_code = None

    def get_transitions_by_input(self, exchange):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start(default_state_value=False)
        >>> r_tm = c.state_machine.transitions[0].incoming[0].factory()
        >>> transition_list = c.get_transitions_by_input([r_tm])
        >>> transition_list[0] == c.state_machine.transitions[0], transition_list[1] == c.state_machine.transitions[3]
        (True, True)
        """
        transition_list = []
        for _t in self.state_machine.transitions:
            if (_t.is_matching_initial(self.states) and
                _t.is_matching_incoming(exchange)):
                transition_list.append(_t)
        return transition_list

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
                return _t
        return None

    def start(self, default_state_value=True):
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
            cls = checkmate._module.get_class_implementing(interface)
            self.states.append(cls.start(default=default_state_value))
        self.service_registry.register(self, self.service_interfaces)
        self.default_state_value = default_state_value

    def reset(self):
        self.pending_incoming = []
        self.pending_outgoing = []
        self.expected_return_code = None
        self.validation_list.clear()

    def stop(self):
        pass

    @checkmate.fix_issue("checkmate/issues/process_pending_incoming.rst")
    def process(self, exchange, transition=None):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start()
        >>> transition=c.state_machine.transitions[0]
        >>> transition.is_matching_initial(c.states)
        True
        >>> output = transition.process(c.states, [sample_app.exchanges.Action("AC")])
        >>> output[0].value
        'RE'
        >>> output[1].value
        True
        >>> transition.is_matching_initial(c.states)
        False
        """
        output = self.process_pending_outgoing()
        if self.expected_return_code is None:
            if len(self.pending_incoming) > 0:
                output = self.process_pending_incoming(output)
            output.extend(self._do_process(exchange, transition))
        else:
            if isinstance(exchange[0], self.expected_return_code.return_type):
                self.expected_return_code = None
                output = self._do_process(exchange, transition)
                output = self.process_pending_incoming(output)
            else:
                self.pending_incoming.append(exchange[0])

        return output

    def process_pending_incoming(self, output):
        for _incoming in self.pending_incoming[:]:
            _incremental_output = self._do_process([_incoming])
            output.extend(_incremental_output)
            self.pending_incoming.remove(_incoming)
            if len([_e for _e in _incremental_output if _e.data_returned]) == 0:
                break
        return output

    def process_pending_outgoing(self):
        output = self.pending_outgoing
        self.pending_outgoing = []
        return output

    def _do_process(self, exchange, transition=None):
        """"""
        if transition is None:
            try:
                _transition = self.get_transitions_by_input(exchange)[0]
            except IndexError:
                if (exchange[0].return_code and self.expected_return_code is not None and
                    isinstance(exchange[0], self.expected_return_code.return_type)):
                    self.expected_return_code = None
                    return self.process_pending_outgoing()
                raise checkmate.exception.NoTransitionFound("No transition for incoming %s " %(exchange[0]))
        else:
            _transition = transition
        output = []
        self.validation_list.record(_transition, exchange)
        for _outgoing in _transition.process(self.states, exchange, default=self.default_state_value):
            for _e in self.service_registry.server_exchanges(_outgoing, self.name):
                if isinstance(_e, exchange[0].return_type):
                    _e._return_code = True
                output.append(_e)
        if exchange[0].data_returned:
            if len([_o for _o in output if _o.return_code]) == 0:
                return_exchange = exchange[0].return_type()
                return_exchange._return_code = True
                return_exchange.origin_destination(self.name, exchange[0].origin)
                output.insert(0, return_exchange)
        for _index, _e in enumerate(output):
            if _e.data_returned:
                self.expected_return_code = _e
                self.pending_outgoing.extend(output[_index+1:])
                output = output[:_index+1]
                break
        return output

    @checkmate.report_issue("checkmate/issues/simulate_return_code.rst")
    def simulate(self, _transition):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c2 = a.components['C2']
            >>> c2.start()
            >>> exchange = sample_app.exchanges.Action('AC')
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
        _incoming = _transition.generic_incoming(self.states)
        for _outgoing in _transition.process(self.states, _incoming, default=self.default_state_value):
            for _e in self.service_registry.server_exchanges(_outgoing, self.name):
                if len(_incoming) != 0 and isinstance(_e, _incoming[0].return_type):
                    continue
                output.append(_e)
        return output

    def validate(self, _transition):
        """
            >>> import sample_app.application
            >>> import sample_app.component.component_1
            >>> a = sample_app.application.TestData()
            >>> c1 = a.components['C1']
            >>> c1.start()
            >>> exchange = sample_app.exchanges.Action('AC')
            >>> transition = c1.get_transitions_by_input([exchange])[0]
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

