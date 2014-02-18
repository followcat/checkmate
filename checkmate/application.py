import os
import collections

import zope.interface

import checkmate._utils
import checkmate.exchange
import checkmate.test_plan
import checkmate.data_structure
import checkmate.parser.dtvisitor
import checkmate.partition_declarator
import checkmate.parser.feature_visitor


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
    def __init__(self):
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

    def build_test_plan(self):
        """"""
        # Take 2 sec
        #self.start()

        self.test_plan = checkmate.test_plan.TestPlan(self.components)

    def get_initial_transitions(self):
        """
            >>> import sample_app.application
            >>> import checkmate.component
            >>> import os
            >>> a = sample_app.application.TestData()
            >>> a.start()
            >>> a.get_initial_transitions()
            >>> a.initial_transitions[0].initial[0].interface
            <InterfaceClass sample_app.component_1.states.IState>
            >>> a.initial_transitions[0].incoming[0].interface
            <InterfaceClass sample_app.exchanges.IAction>
            >>> a.initial_transitions[0].final[2].interface
            <InterfaceClass sample_app.component_3.states.IAcknowledge>
        """
        path = os.path.dirname(self.exchange_module.__file__)
        filename = 'itp.rst'
        _file = open(os.sep.join([path, filename]), 'r')
        matrix = _file.read()
        _file.close()
        _output = checkmate.parser.dtvisitor.call_visitor(matrix)
        state_modules = []
        for name in list(self.components.keys()):
            state_modules.append(self.components[name].state_module)
        self.initial_transitions = []
        for data in _output['transitions']:
            array_items = data['array_items']
            self.initial_transitions.append(checkmate.partition_declarator.new_procedure(array_items, self.exchange_module, state_modules))

    def get_freshen_initial_transitions(self):
        itp_list = checkmate.parser.feature_visitor.get_itp_from_feature(['/home/followcat/Projects/checkmate/sample_app/itp'])
        state_modules = []
        for name in list(self.components.keys()):
            state_modules.append(self.components[name].state_module)
        self.initial_transitions = []
        for data in itp_list:
            self.initial_transitions.append(checkmate.parser.feature_visitor.feature_new_produce(data, self.exchange_module, state_modules))
