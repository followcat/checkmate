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
import checkmate.component
import checkmate.pathfinder
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
        _component_registry = {}
        for class_definition in _component_classes:
            class_dict = class_definition['attributes']
            _tmp_list = class_definition['class'].split('/')
            class_name = _tmp_list[-1].split('.')[0].capitalize()
            alternative_package = _tmp_list[-2]
            component_module = \
                checkmate._module.get_module(namespace['__module__'],
                    class_name.lower(), alternative_package)
            _component_registry[class_name] = []
            for _instance in class_definition['instances']:
                _component_registry[class_name].append(_instance['name'])
            d = {'exchange_module': exchange_module,
                 'data_structure_module': data_structure_module,
                 'component_definition': class_definition['class'],
                 '__module__': component_module.__name__,
                 'communication_list': namespace['communication_list'].keys(),
                 'instances': class_definition['instances']
                }
            d.update(class_dict)
            _class = checkmate.component.ComponentMeta(class_name,
                        (checkmate.component.Component,), d)
            setattr(component_module, class_name, _class)
            class_definition['class'] = _class

        namespace['component_registry'] = _component_registry
        result = type.__new__(cls, name, bases, dict(namespace))
        return result


class Application(object):
    _matrix = numpy.matrix([])
    _matrix_runs = []
    _runs_found = [False]
    component_classes = []
    communication_list = {}
    component_registry = {}
    feature_definition_path = None
    _run_collection_attribute = '_collected_runs'
    _origin_exchanges_attribute = '_origin_exchanges'

    @classmethod
    def reset(cls):
        cls._matrix = numpy.matrix([])
        cls._matrix_runs = []
        cls._runs_found = [False]
        if hasattr(cls, cls._run_collection_attribute):
            delattr(cls, cls._run_collection_attribute)
        if hasattr(cls, cls._origin_exchanges_attribute):
            delattr(cls, cls._origin_exchanges_attribute)

    @classmethod
    def run_collection(cls):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> cls = sample_app.application.TestData
        >>> a.run_collection() #doctest: +ELLIPSIS
        [<checkmate.runs.Run object at ...
        """
        if not hasattr(cls, cls._run_collection_attribute):
            app = cls()
            collection = [_run for _run in app.origin_runs_gen()]
            setattr(cls, cls._run_collection_attribute, collection)
        return getattr(cls, cls._run_collection_attribute)

    @classmethod
    def origin_exchanges(cls):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> exchanges = a.origin_exchanges()
        >>> [ex.value for ex in exchanges]
        ['PBAC', 'PBRL', 'PBPP']
        """
        if not hasattr(cls, cls._origin_exchanges_attribute):
            exchanges = checkmate.runs.get_origin_exchanges(cls)
            setattr(cls, cls._origin_exchanges_attribute, exchanges)
        return getattr(cls, cls._origin_exchanges_attribute)

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
        ...    'attributes': {'class_destination':['Component_1']},
        ...    'define_attributes': {}
        ... }
        >>> app.define_exchange(data_source)
        >>> app.exchange_module.ForthAction.class_destination
        ['Component_1']
        >>> hasattr(app.exchange_module, 'ForthAction')
        True
        >>> delattr(app.exchange_module, 'ForthAction')
        """
        if definition is not None:
            declarator = checkmate.partition_declarator.Declarator(
                            cls.data_structure_module, cls.exchange_module)
            if 'attributes' in definition:
                declarator.new_partition(definition, definition['attributes'])
            else:
                declarator.new_partition(definition)
        try:
            delattr(cls, cls._starting_run_attribute)
            delattr(cls, cls._run_collection_attribute)
            cls._matrix = None
            cls._runs_found = []
        except AttributeError:
            pass

    @checkmate.report_issue('checkmate/issues/run_collect_multi_instances.rst')
    @checkmate.fix_issue('checkmate/issues/match_R2_in_runs.rst')
    @checkmate.fix_issue('checkmate/issues/get_runs_from_failed_simulate.rst')
    @checkmate.report_issue('checkmate/issues/execute_AP_R_AP_R2.rst',
                                failed=3)
    def origin_runs_gen(self):
        """
            >>> import sample_app.application
            >>> cls = sample_app.application.TestData
            >>> app = cls()
            >>> app.start()
            >>> origin_runs = [_r for _r in app.origin_runs_gen()]
            >>> len(origin_runs)
            4
        """
        cls = type(self)
        if hasattr(cls, cls._run_collection_attribute):
            runs = getattr(cls, cls._run_collection_attribute)
            for _r in runs:
                yield _r
            return
        cls.reset()
        exchanges = self.origin_exchanges()
        current_run=None
        yielded_runs = []
        unyielded_runs = []
        box = checkmate.sandbox.Sandbox(cls, self)
        while True:
            _path = []
            next_runs = checkmate.runs.followed_runs(box.application,
                            exchanges, current_run)
            new_next_runs = [_run for _run in next_runs
                                 if _run not in yielded_runs]
            if len(new_next_runs) > 0:
                unyielded_runs.extend([_run for _run in new_next_runs
                                            if _run not in unyielded_runs])
                current_run = new_next_runs[0]
            else:
                if len(unyielded_runs) == 0:
                    break
                current_run, _path = checkmate.pathfinder.find_path(\
                    box.application, unyielded_runs, exchanges, current_run)
            if current_run in unyielded_runs:
                unyielded_runs.remove(current_run)
            for _r in _path + [current_run]:
                box(_r.exchanges)
            current_run = box.blocks
            yielded_runs.append(current_run)
            yield current_run
        setattr(cls, cls._run_collection_attribute, cls._matrix_runs)


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
        self.matrix = None
        self.runs_found = None
        for _class_definition in self.component_classes:
            _class = _class_definition['class']
            for component in _class_definition['instances']:
                _name = component['name']
                self.components[_name] = \
                    _class(_name, self.component_registry)
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

    def copy_states(self):
        copy_states= []
        for _component in list(self.components.values()):
            copy_states.extend(_component.copy_states())
        return copy_states

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

    @classmethod
    def update_matrix(cls, next_runs, current_run):
        """
        notice:update _matrix_runs first then update matrix

        >>> import sample_app.application
        >>> app = sample_app.application.TestData()
        >>> runs = app.run_collection()
        >>> app.reset()
        >>> app._matrix_runs.append(runs[0])  # update _matrix_runs
        >>> app.update_matrix([runs[1]], runs[0])
        >>> app._matrix
        matrix([[0, 1],
                [0, 0]])
        >>> app.update_matrix([runs[2], runs[3]], runs[1])
        >>> app._matrix
        matrix([[0, 1, 0, 0],
                [0, 0, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0]])
        >>> app.update_matrix([runs[1]], runs[2])
        >>> app._matrix
        matrix([[0, 1, 0, 0],
                [0, 0, 1, 1],
                [0, 1, 0, 0],
                [0, 0, 0, 0]])
        >>> app.update_matrix([runs[0]], runs[3])
        >>> app._matrix
        matrix([[0, 1, 0, 0],
                [0, 0, 1, 1],
                [0, 1, 0, 0],
                [1, 0, 0, 0]])
        """
        new_runs = [_run for _run in next_runs \
                    if _run not in cls._matrix_runs]
        extra_length = len(new_runs)
        # extend matrix
        if extra_length > 0:
            if cls._matrix.size == 0:
                cls._matrix = \
                    numpy.matrix([[0]*(extra_length+1)]*(extra_length+1))
            else:
                _temp = cls._matrix.tolist()
                for item in _temp:
                    item.extend([0]*extra_length)
                _temp.extend([[0]*len(_temp[0])]*extra_length)
                cls._matrix = numpy.matrix(_temp)
            cls._matrix_runs.extend(new_runs)
            cls._runs_found.extend([False]*extra_length)
        # update matrix row
        if current_run is not None:
            current_index = cls._matrix_runs.index(current_run)
            row = len(cls._matrix)*[0]
            for _run in next_runs:
                row[cls._matrix_runs.index(_run)] = 1
            cls._matrix[current_index] = row
            cls._runs_found[current_index] = True

