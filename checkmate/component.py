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
import checkmate.tymata.engine
import checkmate.parser.yaml_visitor
import checkmate.partition_declarator


def get_local_update(root_module, definition):
    """"""
    definition_update = {}
    definition_update['class_states'] = []

    try:
        (package_name, file_name) =\
            definition['component_definition'].split('/')[-2:]
        name = file_name.split('.')[0].capitalize()
        definition_update['name'] = name
    except KeyError:
        return definition_update

    exchange_module = definition['exchange_module']
    data_structure_module = definition['data_structure_module']

    (package_name, file_name) =\
         definition['component_definition'].split('/')[-2:]
    name = file_name.split('.')[0].capitalize()
    definition_update['name'] = name

    component_module = \
        checkmate._module.get_module(root_module,
            name.lower(), package_name)
    local_module = component_module.__name__
    definition_update['__module__'] = local_module
    definition_update['component_module'] = component_module

    state_module = checkmate._module.get_module(local_module,
                        name.lower() + '_states')
    definition_update['state_module'] = state_module

    define_data = checkmate.tymata.engine.get_definition_data(
                    definition['component_definition'])
    try:
        data_source = checkmate.parser.yaml_visitor.call_visitor(define_data)
        declarator = checkmate.partition_declarator.Declarator(
                        data_structure_module, exchange_module, state_module)
        declarator.new_definitions(data_source)
        output = declarator.get_output()
        definition_update['class_states'] = output['states']
    except:
        pass

    return definition_update


def get_definition_update(root_module, definition):
    """"""
    definition_update = {}

    try:
        exchange_module = definition['exchange_module']
    except KeyError:
        exchange_module = \
            checkmate._module.get_module(root_module, 'exchanges')
        definition_update['exchange_module'] = exchange_module

    try:
        data_structure_module = definition['data_structure_module']
    except KeyError:
        data_structure_module = \
            checkmate._module.get_module(root_module, 'data_structure')
        definition_update['data_structure_module'] = data_structure_module

    try:
        exchange_definition = definition['exchange_definition']
    except KeyError:
        exchange_definition = os.sep.join(root_module.split('.')[0:-1])
        definition_update['exchange_definition'] = exchange_definition

    data_value = {}
    try:
        value_data = checkmate.tymata.engine.get_definition_data(
                        definition['test_data_definition'])
        value_source = \
            checkmate.parser.yaml_visitor.call_data_visitor(value_data)
        data_value.update(value_source)
        definition_update['data_value'] = data_value
    except KeyError:
        pass

    define_data = checkmate.tymata.engine.get_definition_data(
                    exchange_definition)
    if 'data_structure_definition' in definition:
        define_data += checkmate.tymata.engine.get_definition_data(
                            definition['data_structure_definition'])
    try:
        data_source = checkmate.parser.yaml_visitor.call_visitor(define_data)
        declarator = checkmate.partition_declarator.Declarator(
                        data_structure_module, exchange_module,
                        data_value=data_value)
        declarator.new_definitions(data_source)
        output = declarator.get_output()

        exchanges = output['exchanges']
        data_structure = output['data_structure']
    except:
        exchanges = {}
        data_structure = {}
    finally:
        definition_update['exchanges'] = exchanges
        definition_update['data_structure'] = data_structure

    return definition_update


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
        root_module = namespace['root_module']
        # TODO: use 'definition' key in yaml
        try:
            namespace['component_definition'] = namespace['class']
        except KeyError:
            pass
        definition_update = checkmate.component.get_local_update(
                                root_module, namespace)

        namespace.update(definition_update)
        try:
            name = namespace['name']
        except KeyError:
            pass

        _component_registry = namespace['component_registry']
        _component_registry[name] = []
        instance_attributes = collections.defaultdict(dict)
        namespace['instance_attributes'] = instance_attributes
        namespace['instance_engines'] = collections.defaultdict(dict)
        try:
            block_definitions = [namespace['component_definition']]
        except KeyError:
             block_definitions = []
        try:
            instance_list = namespace['instances']
        except KeyError:
            instance_list = []
        for _instance in instance_list:
            _component_registry[name].append(_instance['name'])

            if 'attributes' in namespace:
                instance_attributes[_instance['name']] = \
                    namespace['attributes']
            if 'attributes' in _instance:
                instance_attributes[_instance['name']].update(
                    _instance['attributes'])

            if 'transitions' in _instance:
                block_definitions.append(_instance['transitions'])
            try:
                _data = checkmate.tymata.engine.get_definition_data(
                            block_definitions)
                blocks = checkmate.tymata.engine.get_blocks_from_data(
                            namespace['exchange_module'],
                            namespace['state_module'],
                            _data)
            except KeyError:
                blocks = []
            services = {}
            service_classes = []
            try:
                communications = set(_instance['communications'])
            except KeyError:
                communications = set()
            for _b in blocks:
                for _i in _b.incoming:
                    _ex = _i.factory()
                    if _i.code not in services:
                        services[_i.code] = _ex
                    if _i.partition_class not in service_classes:
                        service_classes.append(_i.partition_class)
            instance_attributes[_instance['name']].update({
                'services': services,
                'service_classes': service_classes,
                'communications': communications})

            engine = \
                checkmate.tymata.engine.AutoMata(_instance['name'], blocks)
            namespace['instance_engines'][_instance['name']] = engine

        result = type.__new__(cls, name, bases, dict(namespace))
        try:
            setattr(namespace['component_module'], name, result)
        except KeyError:
            pass
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
        self.pending_incoming = []
        self.pending_outgoing = []
        self.default_state_value = True
        self.expected_return_code = None
        self.engine = self.instance_engines[name]
        for _k, _v in self.instance_attributes[name].items():
            setattr(self, _k, _v)
    
    def setup(self):
        """
            >>> import sample_app.application
            >>> app = sample_app.application.TestData()
            >>> c2 = app.components['C2']
            >>> c2.communications
            set()
            >>> c2.setup()
            >>> sorted(c2.communications)
            ['', 'interactive']
        """
        for _b in self.engine.blocks:
            for _io in _b.incoming + _b.outgoing:
                if hasattr(_io, 'partition_class'):
                    self.communications.add(_io.partition_class.communication)
        for _communication in self.communications:
            if (_communication not in self.communication_list
                    and hasattr(self, 'launch_command')):
                # if 'launch_command' is set,
                # communication should be set as well
                raise KeyError(
                    "Communication '%s' is not defined in application"
                    % _communication)

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

    def copy_states(self):
        states = []
        for index, _s in enumerate(self.states):
            states.append(type(_s)())
            states[index].carbon_copy(_s)
        return states

    def _do_process(self, exchange, block=None):
        """"""
        try:
            _block, outgoing = self.engine.process(exchange, self.states,
                                                 self.default_state_value,
                                                 block)
        except IndexError:
            if (exchange[0].return_code and
                    self.expected_return_code is not None and
                    isinstance(exchange[0],
                        self.expected_return_code.return_type)):
                self.expected_return_code = None
                return self.process_pending_outgoing()
            raise checkmate.exception.NoBlockFound(
                "No block for incoming %s " % exchange[0])
        output = []
        for _outgoing in outgoing:
            for new_exchange in self.exchange_destination(_outgoing):
                if isinstance(new_exchange, exchange[0].return_type):
                    new_exchange._return_code = True
                output.append(new_exchange)
        _states = self.copy_states()
        self.validation_dict.record(tuple([tuple(exchange), tuple(_states)]))
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

        Now no matter destination component started or not,we can always
        simulate a transition and get the destination.
            >>> out = c2.simulate(block)
            >>> out[0].value == 'AC'
            True

        Registration is done when the destination component is started:
            >>> a.components['C1'].start()
            >>> out = c2.simulate(block)
            >>> out[0].value == 'AC'
            True
        """
        output = []
        for _outgoing in self.engine.simulate(block, self.states,
                                              self.default_state_value):
            for new_exchange in self.exchange_destination(_outgoing):
                output.append(new_exchange)
        return output

    def validate(self, items):
        """
            >>> import sample_app.application
            >>> import sample_app.component.component_1
            >>> a = sample_app.application.TestData()
            >>> c1 = a.components['C1']
            >>> c1.start()
            >>> exchange = sample_app.exchanges.Action('AC')
            >>> items = tuple([tuple([exchange]), tuple(c1.states)])
            >>> c1.validate(items)
            False
            >>> out = c1.process([exchange])
            >>> c1.validate(items)
            True
            >>> c1.validate(items)
            False
        """
        return self.validation_dict.check(items)

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
