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
        >>> a.application_definition['exchange_definition']
        'sample_app/exchanges.yaml'
        >>> len(a.data_structure) #doctest: +ELLIPSIS
        3
        """
        root_module = namespace['__module__']
        try:
            definition = namespace['application_definition']
        except KeyError:
            definition = {}

        definition_update = checkmate.component.get_definition_update(
                                root_module, definition)

        for key in ('itp_definition', 'feature_definition_path'):
            if key not in definition:
                if key == 'feature_definition_path':
                    pass
                else:
                    definition_update[key] =\
                        os.sep.join(root_module.split('.')[0:-1])

        _component_registry = {}
        try:
            _component_classes = definition['component_classes']
        except KeyError:
            _component_classes = {}

        for class_definition in _component_classes:
            component_namespace = {}
            component_namespace.update(definition_update)
            component_namespace.update(class_definition)
            component_namespace.update({
                'root_module': root_module,
                'component_registry': _component_registry,
                'communication_list': namespace['communication_list']
                })
            _class = checkmate.component.ComponentMeta('_filled_later',
                        (checkmate.component.Component,), component_namespace)
            class_definition['class_from_meta'] = _class

        namespace.update(definition_update)
        namespace['component_classes'] = _component_classes
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
            collection = [_run for _run in 
                checkmate.runs.origin_runs_generator(app)]
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


    @checkmate.report_issue("checkmate/issues/no_data_application_sut.rst",
        failed=2)
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
            _class = _class_definition['class_from_meta']
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

