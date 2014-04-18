import collections

import checkmate.runs
import checkmate.sandbox
import checkmate.runtime.procedure


def get_path_from_pathfinder(application, target):
    """
        >>> import zope.interface
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
        >>> ex1 = sample_app.exchanges.AC()
        >>> ex1.origin_destination('C2', 'C1')
        >>> exchanges = box.generate([ex1])
        >>> app = box.application
        >>> app.components['C3'].states[0].value
        'True'
        >>> checkmate.runtime.registry.global_registry.registerUtility(app, checkmate.application.IApplication)
        >>> proc = sample_app.runtime.test_procedure.TestProcedureRun1Threaded(_class)
        >>> setup = checkmate.runtime.pathfinder.get_path_from_pathfinder(app, proc.initial)
        >>> for _s in setup:
        ...     print(_s.exchanges.root.action, app.compare_states(_s.initial))
        RL True
        PP False
    """
    path = []
    for _run, _app in _find_runs(application, target).items():
        proc = checkmate.runtime.procedure.Procedure(is_setup=True)
        _app.fill_procedure(proc)
        path.append(proc)
    return path

def _find_runs(application, target):
    """
        >>> import checkmate.runs
        >>> import checkmate.sandbox
        >>> import sample_app.application
        >>> import checkmate.runtime.test_plan
        >>> import checkmate.runtime.pathfinder
        >>> a = sample_app.application.TestData()
        >>> runs = a.run_collection
        >>> ac_run = [r for r in runs if r.root.outgoing[0].code == 'AC'][0]
        >>> rl_run = [r for r in runs if r.root.outgoing[0].code == 'RL'][0]

        >>> box = checkmate.sandbox.Sandbox(a)
        >>> box([ac_run.root, rl_run.root])
        True
        >>> proc = []
        >>> for p in checkmate.runtime.test_plan.TestProcedureInitialGenerator():
        ...     proc.append(p)
        ...     

        >>> nbox = checkmate.sandbox.Sandbox(box.application)
        >>> proc[0][0].exchanges.root.action
        'AC'
        >>> len(checkmate.runtime.pathfinder._find_runs(box.application, proc[0][0].initial))
        1
        >>> len(checkmate.runtime.pathfinder._find_runs(box.application, proc[2][0].initial))
        2
        >>> len(checkmate.runtime.pathfinder._find_runs(box.application, proc[3][0].initial))
        3

    """
    used_runs = _next_run(application, target, application.run_collection, collections.OrderedDict())
    return used_runs

def _next_run(application, target, runs, used_runs):
    box = checkmate.sandbox.Sandbox(application)
    for _run in runs:
        if _run in used_runs:
            continue
        box([_run.root])
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
