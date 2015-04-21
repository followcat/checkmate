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
import checkmate.engine
import checkmate.exception
import checkmate.interfaces


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

        def add_definition(namespace, source_files):
            return_dict = {}
            try:

                engine = checkmate.engine.Engine(
                    data_structure_module, exchange_module,
                    state_module, source_files)
                return_dict['engine'] = engine
                return_dict['services'] = engine.services
                return_dict['service_classes'] = engine.service_classes
                return_dict['communication_list'] = engine.communication_list
                for _communication in engine.communication_list:
                    if (_communication not in namespace['communication_list']
                            and 'launch_command' in namespace):
                        # if 'launch_command' is set,
                        # communication should be set as well
                        raise KeyError(
                            "Communication '%s' is not defined in application"
                            % _communication)
                return return_dict
            except Exception as e:
                raise e
        fullfilename = [namespace['component_definition']]
        namespace.update(add_definition(namespace, fullfilename))
        instance_engines = collections.defaultdict(dict)
        for _i, _t in namespace['instance_engines'].items():
            definition_data = ''
            fullfilenames = list()
            for (dirpath, dirnames, filenames) in os.walk(_t):
                for _file in filenames:
                    if _file.endswith(".yaml"):
                        _file = os.path.join(dirpath, _file)
                        fullfilenames.append(_file)
            if definition_data != '':
                instance_namespace = add_definition(namespace, fullfilenames)
                instance_engines[_i] = instance_namespace
        namespace['instance_engines'] = instance_engines
        result = type.__new__(cls, name, bases, dict(namespace))
        return result


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
        self.validation_dict = checkmate._validation.ValidationDict()
        self.service_registry = service_registry
        self.pending_incoming = []
        self.pending_outgoing = []
        self.default_state_value = True
        self.expected_return_code = None
        for _k, _v in self.instance_attributes[name].items():
            setattr(self, _k, _v)
        self.engine.set_owner(name)

    def block_by_name(self, name):
        return self.engine.block_by_name(name)

    def get_blocks_by_input(self, exchange):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start(default_state_value=False)
        >>> r_tm = c.engine.transitions[0].incoming[0].factory()
        >>> transition_list = c.get_blocks_by_input([r_tm])
        >>> transition_list[0] == c.engine.transitions[0]
        True
        >>> transition_list[1] == c.engine.transitions[3]
        True
        """
        return self.engine.get_blocks_by_input(exchange, self.states)

    def get_blocks_by_output(self, exchange):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start()
        >>> for service in c.service_classes:
        ...    print(c.service_registry._registry[service])
        ['C1']
        >>> _t = c.engine.transitions[0]
        >>> r_tm = _t.outgoing[0].factory()
        >>> c.get_blocks_by_output([r_tm]) == _t
        True
        """
        return self.engine.get_blocks_by_output(exchange, self.states)

    @checkmate.fix_issue("checkmate/issues/set_component_attribute_state.rst")
    @checkmate.report_issue(
        "checkmate/issues/validate_initializing_transition.rst", failed=1)
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
        for state in self.engine.states:
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
        self.service_registry.register(self, self.service_classes)
        self.default_state_value = default_state_value
        outgoing = []
        for transition in self.engine.transitions:
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
        >>> transition=c.engine.transitions[0]
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
                _transition = self.get_blocks_by_input(exchange)[0]
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
            for _e in self.service_registry.server_exchanges(_outgoing,
                        self.name):
                if isinstance(_e, exchange[0].return_type):
                    _e._return_code = True
                output.append(_e)
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
            >>> transition = c2.get_blocks_by_output([exchange])

        We can't simulate a transition when no destination for outgoing
        is registered:
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
        for _outgoing in _transition.process(self.states, _incoming,
                            default=self.default_state_value):
            for _e in self.service_registry.server_exchanges(_outgoing,
                        self.name):
                if (len(_incoming) != 0 and
                        isinstance(_e, _incoming[0].return_type)):
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
            >>> transition = c1.get_blocks_by_input([exchange])[0]
            >>> c1.validate(transition)
            False
            >>> out = c1.process([exchange])
            >>> c1.validate(transition)
            True
            >>> c1.validate(transition)
            False
        """
        return self.validation_dict.check(_transition)
