import zope.interface

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
        >>> a.exchange_definition_file
        'sample_app/exchanges.yaml'
        >>> len(a.data_structure) #doctest: +ELLIPSIS
        3
        >>> c1 = a.components['C1']
        >>> c2 = a.components['C2']
        >>> c3 = a.components['C3']
        >>> c1.broadcast_map
        {}
        >>> c2.broadcast_map
        {'PA': 'C1'}
        >>> c3.broadcast_map
        {'PA': 'C1'}
        """
        exchange_module = checkmate._module.get_module(namespace['__module__'], 'exchanges')
        namespace['exchange_module'] = exchange_module

        data_structure_module = checkmate._module.get_module(namespace['__module__'], 'data_structure')
        data_value_module = checkmate._module.get_module(namespace['__module__'], '_data')
        namespace['data_structure_module'] = data_structure_module

        if 'exchange_definition_file' not in namespace:
            #will also be used to look for components' stae_machine yaml and itp.yaml
            namespace['exchange_definition_file'] = namespace['__module__']
        with open(namespace['exchange_definition_file'], 'r') as _file:
            define_data = _file.read()
        with open(namespace['test_data_definition_file'], 'r') as _file:
            value_data = _file.read()
        value_source = checkmate.parser.yaml_visitor.call_data_visitor(value_data)
        data_value = {}
        for code, structure in value_source.items():
            data_value.update({code: (data_structure_module, structure)})
        namespace['data_value'] = data_value
        data_source = checkmate.parser.yaml_visitor.call_visitor(define_data)
        try:
            setattr(checkmate.partition_declarator.Declarator, 'data_value', namespace['data_value'])
            declarator = checkmate.partition_declarator.Declarator(data_structure_module, exchange_module)
            declarator.new_definitions(data_source)
            output = declarator.get_output()

            namespace['data_structure'] = output['data_structure']
            namespace['exchanges'] = output['exchanges']
        finally:
            pass

        for key, (class_name, class_dict) in namespace['component_classes'].items():
            component_module = checkmate._module.get_module(namespace['__module__'], class_name.lower(), 'component')
            d = {'exchange_module': exchange_module,
                 'data_structure_module': data_structure_module,
                 'exchange_definition_file': namespace['exchange_definition_file'],
                 '__module__': component_module.__name__,
                 'connector_list': [_c.connector_class for _c in namespace['communication_list']]
                }
            d.update(class_dict)
            _class = checkmate.component.ComponentMeta(class_name, (checkmate.component.Component,), d)
            setattr(component_module, class_name, _class)
            namespace['component_classes'][key] = _class
            
        publish_map = {}
        for _name_tuple in namespace['component_classes']:
            for _name in _name_tuple:
                publish_map[_name] = namespace['component_classes'][_name_tuple].publish_exchange
        for _c in namespace['component_classes']:
            broadcast_map = {}
            for _e in namespace['component_classes'][_c].subscribe_exchange:
                for _name, _p in publish_map.items():
                    if _e in _p:
                        broadcast_map[_e] = _name
            setattr(namespace['component_classes'][_c], 'broadcast_map', broadcast_map)
            
        result = type.__new__(cls, name, bases, dict(namespace))
        return result


class IApplication(zope.interface.Interface):
    """"""

@zope.interface.implementer(IApplication)
class Application(object):
    component_classes = {}
    communication_list = ()
    feature_definition_path = None

    def __init__(self):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> a.name
        'sample_app'
        >>> len(a.components)
        4
        """
        self.name = self.__module__.split('.')[-2]
        self.components = {}
        self.service_registry = checkmate.service_registry.ServiceRegistry()
        for components, _class in self.component_classes.items():
            for _c in components:
                self.components[_c] = _class(_c, self.service_registry)

    def __getattr__(self, name):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> a.run_collection #doctest: +ELLIPSIS
        [<checkmate.runs.TransitionTree object at ...
        >>> a.origin_transitions #doctest: +ELLIPSIS
        [<checkmate.runs.TransitionTree object at ...
        """
        if name == 'run_collection':
            setattr(self, 'run_collection', checkmate.runs.RunCollection())
            self.run_collection.build_trees_from_application(self)
            return self.run_collection
        if name == 'origin_transitions':
            setattr(self, 'origin_transitions', checkmate.runs.RunCollection())
            self.origin_transitions.get_origin_transition(self)
            return self.origin_transitions
        super().__getattr__(self, name)

    def start(self):
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
        for component in list(self.components.values()):
            component.start()

    def sut(self, system_under_test):
        """
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> a.sut(['C1'])
        >>> len(a.stubs)
        3
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

    @checkmate.fix_issue('checkmate/issues/compare_final.rst')
    @checkmate.fix_issue('checkmate/issues/sandbox_final.rst')
    def compare_states(self, target, reference_state_list=None):
        """Comparison between the states of the application's components and a target.

        This comparison is  taking the length of the target into account.
        If a matching state is twice in the target, the comparison will fail.
        This should probably be fixed.
            >>> import sample_app.application
            >>> app = sample_app.application.TestData()
            >>> app.start()
            >>> c1 = app.components['C1']
            >>> c1.states[0].value
            'True'
            >>> t = c1.state_machine.transitions[0]
            >>> t.initial[0].arguments.values
            ('True',)
            >>> app.compare_states(t.initial)
            True
            >>> target = t.initial + t.initial
            >>> app.compare_states(target)
            False
        """
        if len(target) == 0:
            return True

        local_copy = self.state_list()[:]

        incoming_list = []
        if reference_state_list is not None:
            incoming_list = self.validated_incoming_list()

        for _target in target:
            _length = len(local_copy)
            local_copy = _target.match(local_copy, reference_state_list, incoming_list)
            if len(local_copy) == _length:
                return False
        return True

