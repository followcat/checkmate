# This code is part of the checkmate project.
# Copyright (C) 2013 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import checkmate._tree
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
            run_tree = self.find_run_with_incoming(origin, _run, runs)
            if len(run_tree.nodes) != 0:
                #print((((stub_name, stub_run.final), (sut_name, sut_run.initial)), (stub_name, stub_run.outgoing),
                #       ((stub_name, stub_run.final), (sut_name, sut_run.final)), (sut_name, sut_run.outgoing)))
                self.procedure_list.append(checkmate.procedure.Procedure(index, origin, run_tree))
                index += 1

    def find_run_with_incoming(self, origin, input_run, runs):
        next_runs = []
        for destination in self.components:
            if destination == origin:
                continue
            for _run in runs[destination]:
                for incoming_exchange in _run.incoming:
                    if incoming_exchange in input_run.outgoing:
                        incoming_exchange.origin_destination(origin, destination)
                        following_runs = self.find_run_with_incoming(destination, _run, runs)
                        next_runs.append(following_runs)
        return checkmate._tree.Tree(input_run, next_runs)

    def entry_points(self, runs):
        """Return list of runs that have no incoming
        """
        entry_runs = []
        for name in iter(runs):
            for _run in runs[name]:
                if len(_run.incoming) == 0:
                    _run.incoming.append(checkmate.exchange.Exchange(None))
                    _run.incoming[0].origin_destination('', name)
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
