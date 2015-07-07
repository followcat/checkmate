# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os
import collections

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
        >>> c1.exchange_module #doctest: +ELLIPSIS
        <module 'sample_app.exchanges' from ...
        >>> c1.state_module #doctest: +ELLIPSIS
        <module 'sample_app.component.component_1_states' from ...
        """
        exchange_module = namespace['exchange_module']
        data_structure_module = namespace['data_structure_module']

        state_module = checkmate._module.get_module(namespace['__module__'],
                            name.lower() + '_states')
        namespace['state_module'] = state_module

        def add_definition(namespace, data_source):
            return_dict = {}
            try:
                declarator = checkmate.partition_declarator.Declarator(
                                data_structure_module,
                                exchange_module=exchange_module,
                                state_module=state_module)
                declarator.new_definitions(data_source)
                declarator_output = declarator.get_output()
                return_dict['state_machine'] = checkmate.state_machine.StateMachine(
                                                declarator_output['states'],
                                                declarator_output['transitions'])
                services = {}
                service_classes = []
                communication_list = set()
                for _t in declarator_output['transitions']:
                    for _i in _t.incoming:
                        _ex = _i.factory()
                        if _i.code not in services:
                            services[_i.code] = _ex
                        if _i.partition_class not in service_classes:
                            service_classes.append(_i.partition_class)
                        communication_list.add(_ex.communication)
                    for _o in _t.outgoing:
                        _ex = _o.factory()
                        communication_list.add(_ex.communication)
                return_dict['services'] = services
                return_dict['service_classes'] = service_classes
                for _communication in communication_list:
                    if (_communication not in namespace['communication_list'] and
                            'launch_command' in namespace):
                        #if 'launch_command' is set,
                        #communication should be set as well
                        raise KeyError(
                            "Communication '%s' is not defined in application" %
                            _communication)
                return_dict['communication_list'] = communication_list
                return return_dict
            except Exception as e:
                raise e
        fullfilename = namespace['component_definition']
        with open(fullfilename, 'r') as _file:
            define_data = _file.read()
        data_source = checkmate.parser.yaml_visitor.call_visitor(define_data)
        namespace.update(add_definition(namespace, data_source))
        instance_transitions = collections.defaultdict(dict)
        for _i, _t in namespace['instance_transitions'].items():
            definition_data = ''
            for (dirpath, dirnames, filenames) in os.walk(_t):
                for _file in filenames:
                    if _file.endswith(".yaml"):
                        _file = os.path.join(dirpath, _file)
                        with open(_file, 'r') as open_file:
                            definition_data += open_file.read()
            if definition_data != '':
                data_source = \
                    checkmate.parser.yaml_visitor.call_visitor(definition_data)
                instance_namespace = add_definition(namespace, data_source)
                instance_transitions[_i] = instance_namespace
        namespace['instance_transitions'] = instance_transitions
        result = type.__new__(cls, name, bases, dict(namespace))
        return result


@zope.interface.implementer(checkmate.interfaces.IComponent)
class Component(object):
    def __init__(self, name, component_registry=None):
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
        self.validation_dict = checkmate._validation.ValidationDict()
        self.component_registry = component_registry
        for _tr in self.state_machine.transitions:
            _tr.owner = self.name
        self.pending_incoming = []
        self.pending_outgoing = []
        self.default_state_value = True
        self.expected_return_code = None
        for _k, _v in self.instance_attributes[name].items():
            setattr(self, _k, _v)
        for _k, _v in self.instance_transitions[name].items():
            if _k == 'state_machine':
                self.state_machine.transitions.extend(_v.transitions)
                self.state_machine.transitions = \
                    list(set(self.state_machine.transitions))
            if _k == 'service_classes':
                for _c in _v:
                    if _c not in self.service_classes:
                        self.service_classes.append(_c)
            if _k in ['services', 'communication_list']:
                _attribute = getattr(self, _k)
                _attribute.update(_v)
                setattr(self, _k, _attribute) 

    def transition_by_name(self, name):
        for _t in self.state_machine.transitions:
            if _t.name == name:
                return _t

    def get_transitions_by_input(self, exchange):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start(default_state_value=False)
        >>> r_tm = c.state_machine.transitions[0].incoming[0].factory()
        >>> transition_list = c.get_transitions_by_input([r_tm])
        >>> transition_list[0] == c.state_machine.transitions[0]
        True
        >>> transition_list[1] == c.state_machine.transitions[3]
        True
        """
        transition_list = []
        for _t in self.state_machine.transitions:
            if (_t.is_matching_incoming(exchange, self.states) and
                    _t.is_matching_initial(self.states)):
                transition_list.append(_t)
        return transition_list

    def get_transition_by_output(self, exchange):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start()
        >>> _t = c.state_machine.transitions[0]
        >>> r_tm = _t.outgoing[0].factory()
        >>> c.get_transition_by_output([r_tm]) == _t
        True
        """
        for _t in self.state_machine.transitions:
            if (_t.is_matching_outgoing(exchange) and
                    _t.is_matching_initial(self.states)):
                return _t
        return None

    @checkmate.fix_issue("checkmate/issues/set_component_attribute_state.rst")
    @checkmate.fix_issue(
        "checkmate/issues/validate_initializing_transition.rst")
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
        for state in self.state_machine.states:
            cls = state.partition_class
            _kws = {}
            try:
                if cls.define_attributes['Definition from'] == 'attribute':
                    kw_attributes = cls.define_attributes['Definition name']
                    for _k, _v in kw_attributes.items():
                        if _k in cls.partition_attribute and hasattr(self, _v):
                            _kws[_k] = getattr(self, _v)
            except KeyError:
                pass
            self.states.append(cls.start(default=default_state_value, kws=_kws))
        self.default_state_value = default_state_value
        outgoing = []
        for transition in self.state_machine.transitions:
            if transition.initializing:
                outgoing.extend(self.simulate(transition))
        if len(outgoing) > 0:
            return outgoing

    def reset(self):
        self.pending_incoming = []
        self.pending_outgoing = []
        self.expected_return_code = None
        self.validation_dict.clear()

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
        >>> output = transition.process(c.states,
        ...             [sample_app.exchanges.Action("AC")])
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
            if len([_e for _e in _incremental_output
                    if _e.data_returned]) == 0:
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
                if (exchange[0].return_code and
                        self.expected_return_code is not None and
                        isinstance(exchange[0],
                            self.expected_return_code.return_type)):
                    self.expected_return_code = None
                    return self.process_pending_outgoing()
                raise checkmate.exception.NoTransitionFound(
                    "No transition for incoming %s " % exchange[0])
        else:
            _transition = transition
        output = []
        self.validation_dict.record(_transition, exchange)
        for _outgoing in _transition.process(self.states, exchange,
                            default=self.default_state_value):
            for new_exchange in self.exchange_destination(_outgoing):
                if isinstance(new_exchange, exchange[0].return_type):
                    new_exchange._return_code = True
                output.append(new_exchange)
        if exchange[0].data_returned:
            if len([_o for _o in output if _o.return_code]) == 0:
                return_exchange = exchange[0].return_type()
                return_exchange._return_code = True
                return_exchange.origin_destination(self.name,
                    exchange[0].origin)
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

        Now no matter destination component started or not,we can always
        simulate a transition and get the destination.
            >>> out = c2.simulate(transition)
            >>> out[0].value == 'AC'
            True
        """
        output = []
        _incoming = _transition.generic_incoming(self.states)
        for _outgoing in _transition.process(self.states, _incoming,
                            default=self.default_state_value):
            for new_exchange in self.exchange_destination(_outgoing):
                if (len(_incoming) != 0 and
                        isinstance(new_exchange, _incoming[0].return_type)):
                    continue
                output.append(new_exchange)
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
        return self.validation_dict.check(_transition)

    def exchange_destination(self, exchange):
        """
        >>> import sample_app.application
        >>> app = sample_app.application.TestData()
        >>> app.start()
        >>> c1 = app.components['C1']
        >>> ac = sample_app.exchanges.Action('AC')
        >>> ac.destination
        ['']
        >>> exchanges = []
        >>> for ex in c1.exchange_destination(ac):
        ...     exchanges.append(ex)
        >>> len(exchanges)
        1
        >>> exchanges[0].destination
        ['C1']
        >>> exchanges[0] == ac
        True
        """
        _destinations = []
        for _class_dest in exchange.class_destination:
            _destinations.extend(self.component_registry[_class_dest])
        if exchange.broadcast:
            _destinations = [_destinations]
        for _d in _destinations:
            new_exchange = \
                exchange.partition_storage.partition_class(exchange)
            new_exchange.carbon_copy(exchange)
            new_exchange.origin_destination(self.name, _d)
            yield new_exchange
