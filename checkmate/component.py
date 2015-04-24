# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import collections

import zope.interface

import checkmate._module
import checkmate._validation
import checkmate.engine
import checkmate.exception
import checkmate.interfaces
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
        instance_attributes = collections.defaultdict(dict)
        for _instance in namespace['instances']:
            if 'attributes' in _instance:
                instance_attributes[_instance['name']] = \
                    _instance['attributes']
        namespace['instance_attributes'] = instance_attributes
        namespace['instance_engines'] = collections.defaultdict(dict)

        class_file = namespace['component_definition']
        with open(class_file, 'r') as _file:
            define_data = _file.read()
        data_source = checkmate.parser.yaml_visitor.call_visitor(define_data)
        declarator = checkmate.partition_declarator.Declarator(
            data_structure_module, exchange_module, state_module)
        declarator.new_definitions(data_source)
        output = declarator.get_output()
        namespace['class_states'] = output['states']
        for _instance in namespace['instances']:
            instance_dir = None
            if 'transitions' in _instance:
                instance_dir = _instance['transitions']
            engine = checkmate.engine.Engine(
                data_structure_module, exchange_module,
                state_module, class_file, instance_dir)
            engine.set_owner(_instance['name'])
            try:
                for _communication in engine.communication_list:
                    if (_communication not in namespace['communication_list']
                            and 'launch_command' in namespace):
                        # if 'launch_command' is set,
                        # communication should be set as well
                        raise KeyError(
                            "Communication '%s' is not defined in application"
                            % _communication)
            except Exception as e:
                raise e
            namespace['instance_engines'][_instance['name']] = engine
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
        self.engine = self.instance_engines[name]
        self.service_classes = self.engine.service_classes
        self.services = self.engine.services
        self.communication_list = self.engine.communication_list
        for _k, _v in self.instance_attributes[name].items():
            setattr(self, _k, _v)

    def block_by_name(self, name):
        return self.engine.block_by_name(name)

    def get_blocks_by_input(self, exchange):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start(default_state_value=False)
        >>> r_tm = c.engine.blocks[0].incoming[0].factory()
        >>> block_list = c.get_blocks_by_input([r_tm])
        >>> block_list[0] == c.engine.blocks[0]
        True
        >>> block_list[1] == c.engine.blocks[3]
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
        >>> _t = c.engine.blocks[0]
        >>> r_tm = _t.outgoing[0].factory()
        >>> c.get_blocks_by_output([r_tm]) == _t
        True
        """
        return self.engine.get_blocks_by_output(exchange, self.states)

    @checkmate.fix_issue("checkmate/issues/set_component_attribute_state.rst")
    @checkmate.report_issue(
        "checkmate/issues/validate_initializing_block.rst", failed=1)
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
        for state in self.class_states:
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
        for block in self.engine.blocks:
            if block.initializing:
                outgoing.extend(self.simulate(block))
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
    def process(self, exchange, block=None):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start()
        >>> block=c.engine.blocks[0]
        >>> block.is_matching_initial(c.states)
        True
        >>> output = block.process(c.states,
        ...             [sample_app.exchanges.Action("AC")])
        >>> output[0].value
        'RE'
        >>> output[1].value
        True
        >>> block.is_matching_initial(c.states)
        False
        """
        output = self.process_pending_outgoing()
        if self.expected_return_code is None:
            if len(self.pending_incoming) > 0:
                output = self.process_pending_incoming(output)
            output.extend(self._do_process(exchange, block))
        else:
            if isinstance(exchange[0], self.expected_return_code.return_type):
                self.expected_return_code = None
                output = self._do_process(exchange, block)
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

    def _do_process(self, exchange, block=None):
        """"""
        if block is None:
            try:
                _block = self.get_blocks_by_input(exchange)[0]
            except IndexError:
                if (exchange[0].return_code and
                        self.expected_return_code is not None and
                        isinstance(exchange[0],
                            self.expected_return_code.return_type)):
                    self.expected_return_code = None
                    return self.process_pending_outgoing()
                raise checkmate.exception.NoBlockFound(
                    "No block for incoming %s " % exchange[0])
        else:
            _block = block
        output = []
        self.validation_dict.record(_block, exchange)
        for _outgoing in _block.process(self.states, exchange,
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
    def simulate(self, block):
        """
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> c2 = a.components['C2']
            >>> c2.start()
            >>> exchange = sample_app.exchanges.Action('AC')
            >>> block = c2.get_blocks_by_output([exchange])

        We can't simulate a block when no destination for outgoing
        is registered:
            >>> c2.simulate(block)
            []

        Registration is done when the destination component is started:
            >>> a.components['C1'].start()
            >>> out = c2.simulate(block)
            >>> out[0].value == 'AC'
            True
        """
        output = []
        _incoming = block.generic_incoming(self.states)
        for _outgoing in block.process(self.states, _incoming,
                            default=self.default_state_value):
            for _e in self.service_registry.server_exchanges(_outgoing,
                        self.name):
                if (len(_incoming) != 0 and
                        isinstance(_e, _incoming[0].return_type)):
                    continue
                output.append(_e)
        return output

    def validate(self, block):
        """
            >>> import sample_app.application
            >>> import sample_app.component.component_1
            >>> a = sample_app.application.TestData()
            >>> c1 = a.components['C1']
            >>> c1.start()
            >>> exchange = sample_app.exchanges.Action('AC')
            >>> block = c1.get_blocks_by_input([exchange])[0]
            >>> c1.validate(block)
            False
            >>> out = c1.process([exchange])
            >>> c1.validate(block)
            True
            >>> c1.validate(block)
            False
        """
        return self.validation_dict.check(block)
