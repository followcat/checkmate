import os

import zope.interface

import checkmate.runs
import checkmate._module
import checkmate.component
import checkmate.partition_declarator


class ApplicationMeta(type):
    def __new__(cls, name, bases, namespace, **kwds):
        data_structure_module = namespace['data_structure_module']
        exchange_module = namespace['exchange_module']

        path = os.path.dirname(exchange_module.__file__)
        filename = 'exchanges.yaml'
        with open(os.sep.join([path, filename]), 'r') as _file:
            matrix = _file.read()
        try:
            global checkmate
            declarator = checkmate.partition_declarator.Declarator(data_structure_module, exchange_module=exchange_module, content=matrix)
            output = declarator.get_output()

            namespace['data_structure'] = output['data_structure']
            namespace['exchanges'] = output['exchanges']
        finally:
            pass

        for key, (class_name, class_dict) in namespace['component_classes'].items():
            component_module = checkmate._module.get_module(namespace['__module__'], class_name.lower(), '.component')
            d = {'exchange_module': exchange_module,
                 'data_structure_module': data_structure_module,
                 '__module__': component_module.__name__,
                 'connector_list': [_c.connector_class for _c in namespace['communication_list']]
                }
            d.update(class_dict)
            _class = checkmate.component.ComponentMeta(class_name, (checkmate.component.Component,), d)
            setattr(component_module, class_name, _class)
            namespace['component_classes'][key] = _class
            
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
        """
        self.name = self.__module__.split('.')[-2]
        self.components = {}
        for components, _class in self.component_classes.items():
            for _c in components:
                self.components[_c] = _class(_c)


    def __getattr__(self, name):
        if name == 'run_collection':
            setattr(self, 'run_collection', checkmate.runs.RunCollection())
            self.run_collection.build_trees_from_application(self)
            return self.run_collection
        super().__getattr__(self, name)

    def start(self):
        """
        """
        for component in list(self.components.values()):
            component.start()

    def sut(self, system_under_test):
        """"""
        self.stubs = list(self.components.keys())
        self.system_under_test = list(system_under_test)
        for name in system_under_test:
            if name not in list(self.components.keys()):
                self.system_under_test.pop(system_under_test.index(name))
            else:
                self.stubs.pop(self.stubs.index(name))

    def compare_states(self, target):
        """"""
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

