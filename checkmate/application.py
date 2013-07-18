import checkmate.exchange
import checkmate.parser.doctree


class Application(object):
    def __init__(self, matrix, exchange_module=None):
        """
        """
        self.exchanges = []
        self.components = {}
        global checkmate
        output = checkmate.parser.doctree.load_partitions(matrix, exchange_module)
        setattr(self, 'exchanges', output['exchanges'])

    def start(self):
        """
        """
        for component in list(self.components.values()):
            component.start()
        

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

        for stub_name in stubs:
            for stub_run in runs[stub_name]:
                for sut_name in system_under_test:
                    for sut_run in runs[sut_name]:
                        if sut_run.incoming in stub_run.outgoing:
                            print((((stub_name, stub_run.final), (sut_name, sut_run.initial)), (stub_name, stub_run.outgoing), ((stub_name, stub_run.final), (sut_name, sut_run.final)), (sut_name, sut_run.outgoing)))
