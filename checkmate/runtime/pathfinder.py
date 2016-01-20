# This code is part of the checkmate project.
# Copyright (C) 2014-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import collections

import checkmate.runs
import checkmate.sandbox
import checkmate.runtime.procedure


def get_path_from_pathfinder(application, target):
    """
        >>> import checkmate.runs
        >>> import checkmate.sandbox
        >>> import checkmate.runtime.registry
        >>> import checkmate.runtime.pathfinder
        >>> import checkmate.runtime.communication
        >>> import sample_app.application
        >>> import sample_app.exchanges
        >>> import sample_app.runtime.test_procedure
        >>> cc = checkmate.runtime.communication.Communication
        >>> _class = sample_app.application.TestData
        >>> runs = checkmate.runs.RunCollection()
        >>> runs.build_trees_from_application(_class())
        >>> r = checkmate.runtime._runtime.Runtime(_class, cc)
        >>> box = checkmate.sandbox.Sandbox(_class())
        >>> ex1 = sample_app.exchanges.Action('AC')
        >>> ex1.origin_destination('C2', 'C1')
        >>> _t = box.application.components['C2'].get_transition_by_output([ex1])
        >>> transitions = box.generate([ex1], checkmate._tree.Tree(_t, []))
        >>> app = box.application
        >>> app.components['C3'].states[0].value
        'True'
        >>> registry = checkmate.runtime.registry.RuntimeGlobalRegistry()
        >>> registry.registerUtility(app, checkmate.application.IApplication)
        >>> proc = sample_app.runtime.test_procedure.TestProcedureRun1Threaded(_class)
        >>> setup = checkmate.runtime.pathfinder.get_path_from_pathfinder(app, proc.initial)
        >>> for _s in setup:
        ...     print(_s.transitions.root.outgoing[0].code, app.compare_states(_s.initial))
        PBRL True
        PBPP False
    """
    path = []
    for _run, _app in _find_runs(application, target).items():
        proc = checkmate.runtime.procedure.Procedure(type(application), is_setup=True)
        _app.fill_procedure(proc)
        path.append(proc)
    return path

def _find_runs(application, target):
    """
        >>> import checkmate.runs
        >>> import checkmate.sandbox
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> import checkmate.runtime.pathfinder
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> runs = a.run_collection
        >>> ac_run = [r for r in runs if r.root.outgoing[0].code == 'PBAC'][0]
        >>> rl_run = [r for r in runs if r.root.outgoing[0].code == 'PBRL'][0]

        >>> box = checkmate.sandbox.Sandbox(a)
        >>> box(ac_run.root)
        True
        >>> box(rl_run.root)
        True
        >>> proc = []
        >>> for p in checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData):
        ...     proc.append(p)
        ...     

        >>> proc[0][0].transitions.root.outgoing[0].code
        'AC'
        >>> len(checkmate.runtime.pathfinder._find_runs(box.application, proc[0][0].initial))
        3

    """
    used_runs = _next_run(application, target, application.origin_transitions, collections.OrderedDict())
    return used_runs


def _next_run(application, target, runs, used_runs):
    """
        >>> import collections
        >>> import checkmate.sandbox
        >>> import checkmate.runtime.test_plan
        >>> import checkmate.runtime.pathfinder
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> box = checkmate.sandbox.Sandbox(a)
        >>> proc = []
        >>> for p in checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData):
        ...     proc.append(p)

        >>> proc[0][0].transitions.root.outgoing[0].code
        'AC'
        >>> [_t.root.outgoing[0].code for _t in checkmate.runtime.pathfinder._next_run(box.application, proc[0][0].initial, a.origin_transitions, collections.OrderedDict())]
        ['PBAC', 'PBRL', 'PBPP']

        >>> proc[3][0].transitions.root.outgoing[0].code
        'PP'
        >>> [_t.root.outgoing[0].code for _t in checkmate.runtime.pathfinder._next_run(box.application, proc[3][0].initial, a.origin_transitions, collections.OrderedDict())]
        ['PBAC', 'PBRL']

    """
    box = checkmate.sandbox.Sandbox(application)
    for _run in runs:
        if _run in used_runs:
            continue
        box(_run.root)
        if box.is_run:
            if box.application.compare_states(target):
                used_runs[_run] = box
                return used_runs
            else:
                used_runs.update({_run: box})
                returned_runs = _next_run(box.application, target, runs, used_runs)
                if len(returned_runs) == 0:
                    del used_runs[_run]
                    box = checkmate.sandbox.Sandbox(application)
                    continue
                else:
                    return returned_runs
    return collections.OrderedDict()
