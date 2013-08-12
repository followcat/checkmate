import os

import checkmate.data_structure
import checkmate.exchange
import checkmate.procedure
import checkmate.parser.dtvisitor
import checkmate.parser.rst_writer
import checkmate.partition_declarator


def define_procedure(index, stub_name, stub_run, sut_name, sut_run):
    """"""
    name = 'TestProcedure_{index}'.format(index=index)
    path = 'integration/procedures/test_{sut}.py'.format(sut=sut_name)
    _class = 'Test{sut}{state}{incoming}'.format(sut=sut_name,state=''.join([i.partition_id for i in sut_run.initial]), incoming = sut_run.desc_incoming)
    history = ['Now']
 
    initial_state = [s.partition_id for s in sut_run.initial]
 
    final_state = [s.partition_id for s in sut_run.final]
 
    exchanges = [[sut_run.incoming.partition_id, sut_run.incoming.origin, sut_run.incoming.destination, sut_run.desc_incoming]]
    for o in sut_run.final:
        if (o.partition_id != sut_run.initial[sut_run.final.index(o)].partition_id):
            exchanges.append([o.partition_id, sut_name, sut_name, sut_run.desc_final[sut_run.final.index(o)]])
 
    for o in sut_run.outgoing:
        exchanges.append([o.partition_id, sut_name, stub_name, sut_run.desc_outgoing[sut_run.outgoing.index(o)]])
 
    return checkmate.procedure.Procedure(name, path, _class, history=history, initial_state=initial_state, final_state=final_state, exchanges=exchanges)


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
                    self.procedure_list.append(define_procedure(index, stub_name, stub_run, sut_name, sut_run))
                    index += 1



    def itp(self, filename):
        buffer = ""
        f = open(filename, 'w')
        wt = checkmate.parser.rst_writer.Writer()
        for proc in self.procedure_list:
            dt = proc.doctree()
            wt.write(dt, f)
        f.close()
