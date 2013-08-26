import os

import zope.interface

import checkmate.exchange
import checkmate.test_plan
import checkmate.data_structure
import checkmate.parser.dtvisitor
import checkmate.partition_declarator


class ApplicationMeta(type):
    def __new__(cls, name, bases, namespace, **kwds):
        data_structure_module = namespace['data_structure_module']
        exchange_module = namespace['exchange_module']

        path = os.path.dirname(exchange_module.__file__)
        filename = 'exchanges.rst'
        _file = open(os.sep.join([path, filename]), 'r')
        matrix = _file.read()
        _file.close()
        try:
            global checkmate
            declarator = checkmate.partition_declarator.Declarator(data_structure_module, exchange_module=exchange_module)
            output = checkmate.parser.dtvisitor.call_visitor(matrix, declarator)

            namespace['data_structure'] = output['data_structure']
            namespace['exchanges'] = output['exchanges']
        finally:
            result = type.__new__(cls, name, bases, dict(namespace))
            return result


class IApplication(zope.interface.Interface):
    """"""

@zope.interface.implementer(IApplication)
class Application(object):
    def __init__(self):
        """
        """
        self.components = {}
        self.procedure_list = []

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

    def build_test_plan(self):
        """"""
        # Take 2 sec
        #self.start()

        self.test_plan = checkmate.test_plan.TestPlan(self.components)

