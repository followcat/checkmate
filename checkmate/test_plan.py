import checkmate.exchange
import checkmate.procedure
import checkmate.parser.rst_writer


class TestPlan(object):
    def __init__(self, components):
        """"""
        self.components = components
        runs = {}
        for name in list(self.components.keys()):
            runs[name] = []
            for found_run in self.components[name].state_machine.develop(self.components[name].states, []):
                runs[name].append(found_run)

        index = 0
        self.procedure_list = []
        for origin, _run in self.entry_points(runs):
            (sut_name, sut_run) = self.find_run_with_incoming(origin, _run.outgoing, runs)
            if sut_name is not None:
                #print((((stub_name, stub_run.final), (sut_name, sut_run.initial)), (stub_name, stub_run.outgoing),
                #       ((stub_name, stub_run.final), (sut_name, sut_run.final)), (sut_name, sut_run.outgoing)))
                self.procedure_list.append(checkmate.procedure.Procedure(index, origin, sut_name, sut_run))
                index += 1

    def find_run_with_incoming(self, origin, incoming, runs):
        for destination in self.components:
            if destination == origin:
                continue
            for _run in runs[destination]:
                if _run.incoming in incoming:
                    _run.incoming.origin_destination(origin, destination)
                    return (destination, _run)
        return (None, None)

    def entry_points(self, runs):
        """Return list of runs
        """
        entry_runs = []
        for name in iter(runs):
            for _run in runs[name]:
                if _run.incoming == checkmate.exchange.Exchange(None):
                    entry_runs.append((name, _run))
        return entry_runs
                   

    def itp(self, filename):
        buffer = ""
        f = open(filename, 'w')
        wt = checkmate.parser.rst_writer.Writer()
        for proc in self.procedure_list:
            dt = proc.doctree()
            wt.write(dt, f)
        f.close()
