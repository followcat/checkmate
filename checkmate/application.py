import os

import checkmate.data_structure
import checkmate.exchange
import checkmate.procedure
import checkmate.parser.dtvisitor
import checkmate.parser.rst_writer


def define_procedure(index, stub_name, stub_run, sut_name, sut_run):
    def partition_id(i):
        """Return partition id of the given state or exchange"""
        return i[1]

    name = 'TestProcedure_{index}'.format(index=index)
    path = 'integration/procedures/test_{sut}.py'.format(sut=sut_name)
    _class = 'Test{sut}{state}{incoming}'.format(sut=sut_name,state=''.join([partition_id(i) for i in sut_run.initial]), incoming = sut_run.desc_incoming)
    history = ['Now']

    initial_state = [partition_id(s) for s in sut_run.initial]

    final_state = [partition_id(s) for s in sut_run.final]

    exchanges = [[partition_id(sut_run.incoming), stub_name, sut_name, sut_run.desc_incoming]]
    for o in sut_run.final:
        if partition_id(o) != partition_id(sut_run.initial[sut_run.final.index(o)]):
            exchanges.append([partition_id(o), sut_name, sut_name, sut_run.desc_final[sut_run.final.index(o)]])

    for o in sut_run.outgoing:
        exchanges.append([partition_id(o), sut_name, stub_name, sut_run.desc_outgoing[sut_run.outgoing.index(o)]])

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
            output = checkmate.parser.dtvisitor.call_visitor(matrix, data_structure_module=data_structure_module, exchange_module=exchange_module)
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
        
    def sender(self, exchange):
        for exchange_interface in zope.interface.providedBy(exchange):
            found = False
            for transition in self.state_machine.transitions:
                if exchange_interface in [o.interface for o in transition.outgoing]:
                    found = True
                    break
            if found == False:
                return False
        return True


    def test_plan(self, system_under_test):
        """"""
        self.system_under_test = system_under_test

        runs = {}
        stubs = list(self.components.keys())
        for name in system_under_test:
            if name not in list(self.components.keys()):
                self.system_under_test.pop(self.system_under_test.index(name))
            else:
                stubs.pop(stubs.index(name))

        for name in list(self.components.keys()):
            runs[name] = []
            for found_run in self.components[name].state_machine.develop(self.components[name].states):
                runs[name].append(found_run)

        index = 0
        self.procedure_list = []
        for stub_name in stubs:
            for stub_run in runs[stub_name]:
                for sut_name in system_under_test:
                    for sut_run in runs[sut_name]:
                        if sut_run.incoming in stub_run.outgoing:
                            #print((((stub_name, stub_run.final), (sut_name, sut_run.initial)), (stub_name, stub_run.outgoing), ((stub_name, stub_run.final), (sut_name, sut_run.final)), (sut_name, sut_run.outgoing)))
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
