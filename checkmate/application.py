import zope.interface

import checkmate.runs
import checkmate._module
import checkmate.component
import checkmate.service_registry
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
        1
        """
        exchange_module = checkmate._module.get_module(namespace['__module__'], 'exchanges')
        namespace['exchange_module'] = exchange_module

        data_structure_module = checkmate._module.get_module(namespace['__module__'], 'data_structure')
        namespace['data_structure_module'] = data_structure_module

        if 'exchange_definition_file' not in namespace:
            #will also be used to look for components' stae_machine yaml and itp.yaml
            namespace['exchange_definition_file'] = namespace['__module__']
        with open(namespace['exchange_definition_file'], 'r') as _file:
            matrix = _file.read()
        try:
            declarator = checkmate.partition_declarator.Declarator(data_structure_module, exchange_module, content=matrix)
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
            
        for _name in namespace['component_classes']:
            connecting_components = []
            for _n in [_c for _c in namespace['component_classes'] if _c != _name]:
                for service in namespace['component_classes'][_n].services:
                    if service in namespace['component_classes'][_name].outgoings:
                        connecting_components.extend(_n)
                        break
            setattr(namespace['component_classes'][_name], 'connecting_components', connecting_components)
            
        result = type.__new__(cls, name, bases, dict(namespace))
        return result


class IApplication(zope.interface.Interface):
    """"""

@zope.interface.implementer(IApplication)
class Application(object):
    component_classes = {}
    communication_list = ()

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
        """
        if name == 'run_collection':
            setattr(self, 'run_collection', checkmate.runs.RunCollection())
            self.run_collection.build_trees_from_application(self)
            return self.run_collection
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

    @checkmate.report_issue('checkmate/issues/sandbox_final.rst')
    def compare_states(self, target):
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
            >>> t.initial[0].arguments['values']
            ('True',)
            >>> app.compare_states(t.initial)
            True
            >>> target = t.initial + t.initial
            >>> app.compare_states(target)
            False
        """
        if len(target) == 0:
            return True

        local_copy = []
        for _component in list(self.components.values()):
            local_copy += [_s for _s in _component.states]

        for _target in target:
            _length = len(local_copy)
            local_copy = _target.match(local_copy)
            if len(local_copy) == _length:
                return False
        return True

