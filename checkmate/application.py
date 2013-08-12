import os

import checkmate.exchange
import checkmate.procedure
import checkmate.data_structure
import checkmate.parser.dtvisitor
import checkmate.parser.rst_writer
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
        
    def find_run_with_incoming(self, origin, incoming, runs, components):
        for destination in components:
            for _run in runs[destination]:
                if _run.incoming in incoming:
                    _run.incoming.origin_destination(origin, destination)
                    return (destination, _run)
        return (None, None)

    def test_plan(self, system_under_test):
        """"""
        # Take 2 sec
        #self.start()

        runs = {}
        self.stubs = list(self.components.keys())
        self.system_under_test = system_under_test
        for name in system_under_test:
            if name not in list(self.components.keys()):
                self.system_under_test.pop(system_under_test.index(name))
            else:
                self.stubs.pop(self.stubs.index(name))

        for name in list(self.components.keys()):
            runs[name] = []
            for found_run in self.components[name].state_machine.develop(self.components[name].states):
                runs[name].append(found_run)

        index = 0
        self.procedure_list = []
        for stub_name in self.stubs:
            for stub_run in runs[stub_name]:
                (sut_name, sut_run) = self.find_run_with_incoming(stub_name, stub_run.outgoing, runs, self.system_under_test)
                if sut_name is not None:
                    #print((((stub_name, stub_run.final), (sut_name, sut_run.initial)), (stub_name, stub_run.outgoing),
                    #       ((stub_name, stub_run.final), (sut_name, sut_run.final)), (sut_name, sut_run.outgoing)))
                    self.procedure_list.append(checkmate.procedure.Procedure(index, stub_name, sut_name, sut_run))
                    index += 1


    def itp(self, filename):
        buffer = ""
        f = open(filename, 'w')
        wt = checkmate.parser.rst_writer.Writer()
        for proc in self.procedure_list:
            dt = proc.doctree()
            wt.write(dt, f)
        f.close()
