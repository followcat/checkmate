import os
import collections

import zope.interface

import checkmate._utils
import checkmate.exchange
import checkmate.data_structure
import checkmate.parser.dtvisitor
import checkmate.partition_declarator


class ApplicationMeta(type):
    def __new__(cls, name, bases, namespace, **kwds):
        data_structure_module = namespace['data_structure_module']
        exchange_module = namespace['exchange_module']

        path = os.path.dirname(exchange_module.__file__)
        filename = 'exchanges.rst'
        with open(os.sep.join([path, filename]), 'r') as _file:
            matrix = _file.read()
        try:
            global checkmate
            declarator = checkmate.partition_declarator.Declarator(data_structure_module, exchange_module=exchange_module, content=matrix)
            output = declarator.get_output()

            namespace['data_structure'] = output['data_structure']
            namespace['exchanges'] = output['exchanges']
        finally:
            result = type.__new__(cls, name, bases, dict(namespace))
            return result


class IApplication(zope.interface.Interface):
    """"""

@zope.interface.implementer(IApplication)
class Application(object):
    def __init__(self, full_python=False):
        """
        """
        self.components = {}
        self.procedure_list = []
        self.name = self.__module__.split('.')[-2]
        self.communication_list = ()

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
        matching = 0
        for _target in target:
            for _component in list(self.components.values()):
                try:
                    #Assume at most one state of component implements interface
                    _state = [_s for _s in _component.states if _target.interface.providedBy(_s)].pop(0)
                    if _state == _target.factory():
                        matching += 1
                        break
                    else:
                        break
                except IndexError:
                        continue
        return matching == len(target)

