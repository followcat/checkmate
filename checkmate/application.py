# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os
import collections

import numpy

import checkmate.runs
import checkmate._module
import checkmate.sandbox
import checkmate.component
import checkmate.service_registry
import checkmate.parser.yaml_visitor
import checkmate.partition_declarator


class ApplicationMeta(type):
    def __new__(cls, name, bases, namespace, **kwds):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> a.exchange_module #doctest: +ELLIPSIS
        <module 'sample_app.exchanges' from ...
        >>> a.data_structure_module #doctest: +ELLIPSIS
        <module 'sample_app.data_structure' from ...
        >>> a.exchange_definition
        'sample_app/exchanges.yaml'
        >>> len(a.data_structure) #doctest: +ELLIPSIS
        3
        """
        exchange_module = \
            checkmate._module.get_module(namespace['__module__'], 'exchanges')
        namespace['exchange_module'] = exchange_module

        data_structure_module = \
            checkmate._module.get_module(namespace['__module__'],
                'data_structure')
        namespace['data_structure_module'] = data_structure_module

        if 'exchange_definition' not in namespace:
            namespace['exchange_definition'] = \
                os.sep.join(namespace['__module__'].split('.')[0:-1])
        if 'itp_definition' not in namespace:
            namespace['itp_definition'] = \
                os.sep.join(namespace['__module__'].split('.')[0:-1])
        def get_definition_data(definitions):
            definition_data = ''
            if type(definitions) != list:
                definitions = [definitions]
            for _d in definitions:
                if os.path.isfile(_d):
                    with open(_d, 'r') as _file:
                        definition_data += _file.read()
                elif os.path.isdir(_d):
                    for filename in os.listdir(_d):
                        if filename.endswith(".yaml"):
                            _fullname = os.path.join(_d, filename)
                            with open(_fullname, 'r') as _file:
                                definition_data += _file.read()
            return definition_data
        define_data = get_definition_data(namespace['exchange_definition'])
        if 'data_structure_definition' in namespace:
            define_data += \
                get_definition_data(namespace['data_structure_definition'])
        data_value = {}
        try:
            value_data = get_definition_data(namespace['test_data_definition'])
            value_source = \
                checkmate.parser.yaml_visitor.call_data_visitor(value_data)
            for code, structure in value_source.items():
                data_value.update({code: structure})
            namespace['data_value'] = data_value
        except KeyError:
            pass
        data_source = checkmate.parser.yaml_visitor.call_visitor(define_data)
        try:
            declarator = checkmate.partition_declarator.Declarator(
                            data_structure_module, exchange_module,
                            data_value=data_value)
            declarator.new_definitions(data_source)
            output = declarator.get_output()

            namespace['data_structure'] = output['data_structure']
            namespace['exchanges'] = output['exchanges']
        finally:
            pass

        _component_classes = namespace['component_classes']
        for index, _definition in enumerate(_component_classes):
            _tmp_dict = collections.defaultdict(dict)
            _tmp_dict.update(_definition)
            _component_classes[index] = _tmp_dict
        for class_definition in _component_classes:
            class_dict = class_definition['attributes']
            _tmp_list = class_definition['class'].split('/')
            class_name = _tmp_list[-1].split('.')[0].capitalize()
            alternative_package = _tmp_list[-2]
            component_module = \
                checkmate._module.get_module(namespace['__module__'],
                    class_name.lower(), alternative_package)
            instance_attributes = collections.defaultdict(dict)
            instance_transitions = collections.defaultdict(dict)
            for _instance in class_definition['instances']:
                if 'attributes' in _instance:
                    instance_attributes[_instance['name']] = \
                        _instance['attributes']
                if 'transitions' in _instance:
                    instance_transitions[_instance['name']] = \
                        _instance['transitions']
            d = {'exchange_module': exchange_module,
                 'data_structure_module': data_structure_module,
                 'component_definition': class_definition['class'],
                 '__module__': component_module.__name__,
                 'communication_list': namespace['communication_list'].keys(),
                 'instance_attributes': instance_attributes,
                 'instance_transitions': instance_transitions
                }
            d.update(class_dict)
            _class = checkmate.component.ComponentMeta(class_name,
                        (checkmate.component.Component,), d)
            setattr(component_module, class_name, _class)
            class_definition['class'] = _class

        result = type.__new__(cls, name, bases, dict(namespace))
        return result


class Application(object):
    _matrix = None
    _runs_found = []
    component_classes = []
    communication_list = {}
    feature_definition_path = None
    _starting_run_attribute = '_starting_run'
    _run_collection_attribute = '_collected_runs'
    path_finder_depth = 10

    @classmethod
    def run_collection(cls):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> a.run_collection() #doctest: +ELLIPSIS
        [<checkmate.runs.Run object at ...
        """
        if not hasattr(cls, cls._run_collection_attribute):
            collection = checkmate.runs.get_runs_from_application(cls)
            length = len(collection)
            cls._matrix = numpy.matrix(numpy.zeros((length, length), dtype=int))
            cls._runs_found = [False]*length
            setattr(cls, cls._run_collection_attribute, collection)
        return getattr(cls, cls._run_collection_attribute)

    @classmethod
    def define_exchange(cls, definition=None):
        """
        >>> import sample_app.application
        >>> app = sample_app.application.TestData()
        >>> data_source = {
        ...    'partition_type': 'exchanges',
        ...    'signature': 'ForthAction',
        ...    'codes_list': ['AF()'],
        ...    'values_list': ['AF'],
        ...    'attributes': {},
        ...    'define_attributes': {}
        ... }
        >>> app.define_exchange(data_source)
        >>> hasattr(app.exchange_module, 'ForthAction')
        True
        >>> delattr(app.exchange_module, 'ForthAction')
        """
        if definition is not None:
            declarator = checkmate.partition_declarator.Declarator(
                            cls.data_structure_module, cls.exchange_module)
            declarator.new_partition(definition)
        try:
            delattr(cls, cls._starting_run_attribute)
            delattr(cls, cls._run_collection_attribute)
            cls._matrix = None
            cls._runs_found = []
        except AttributeError:
            pass

    @classmethod
    def starting_run(cls):
        try:
            return getattr(cls, cls._starting_run_attribute)
        except AttributeError:
            try:
                for run in cls.run_collection():
                    if run.root.name == cls.starting_run_name:
                        break
            except AttributeError:
                run = cls.run_collection()[-1]
            setattr(cls, cls._starting_run_attribute, run)
            return run

    def __init__(self):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> a.name
        'sample_app'
        >>> len(a.components)
        3
        """
        self.name = self.__module__.split('.')[-2]
        self._started = False
        self.components = collections.OrderedDict()
        self.service_registry = checkmate.service_registry.ServiceRegistry()
        self.matrix = None
        self.runs_found = None
        for _class_definition in self.component_classes:
            _class = _class_definition['class']
            for component in _class_definition['instances']:
                _name = component['name']
                self.components[_name] = \
                    _class(_name, self.service_registry)
        self.default_state_value = True
        self.initializing_outgoing = []

    def start(self, default_state_value=True):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> len(c.states)
        0
        >>> a.start()
        >>> c.states #doctest: +ELLIPSIS
        [<sample_app.component.component_1_states.State object at ...
        """
        if not self._started:
            for component in list(self.components.values()):
                _out = component.start(default_state_value=default_state_value)
                if _out is not None:
                    self.initializing_outgoing.append(_out)
            self._started = True
        self.default_state_value = default_state_value

    def sut(self, system_under_test):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> a.sut(['C1'])
        >>> len(a.stubs)
        2
        """
        self.stubs = list(self.components.keys())
        self.system_under_test = list(system_under_test)
        for name in system_under_test:
            if name not in list(self.components.keys()):
                self.system_under_test.pop(system_under_test.index(name))
            else:
                self.stubs.pop(self.stubs.index(name))

    def state_list(self):
        """Return a static list of the component state values
        """
        local_copy = []
        for _component in list(self.components.values()):
            local_copy += [_s for _s in _component.states]
        return local_copy

    def validated_incoming_list(self):
        incoming_list = []
        for _component in list(self.components.values()):
            incoming_list += _component.get_all_validated_incoming()
        return incoming_list

    def visual_dump_states(self):
        state_dict = {}
        for _c, _v in self.components.items():
            for _s in _v.states:
                if _c not in state_dict:
                    state_dict[_c] = {}
                cls_name = type(_s).__name__
                state_dict[_c][cls_name] = _s._dump()
        return state_dict
