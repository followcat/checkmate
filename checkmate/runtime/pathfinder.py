import collections

import checkmate.sandbox
import checkmate.paths_finder
import checkmate.runtime.procedure


def get_path_from_pathfinder(application, target):
    """
        >>> import zope.interface
        >>> import checkmate.sandbox
        >>> import checkmate.paths_finder
        >>> import checkmate.runtime.registry    
        >>> import checkmate.runtime.pathfinder
        >>> import checkmate.runtime.communication
        >>> import sample_app.application
        >>> import sample_app.exchanges
        >>> import sample_app.runtime.test_procedure
        >>> cc = checkmate.runtime.communication.Communication
        >>> _class = sample_app.application.TestData
        >>> runs = checkmate.paths_finder.RunCollection()
        >>> runs.build_trees_from_application(_class)
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
        >>> generator = checkmate.runtime.pathfinder.get_path_from_pathfinder(app, proc.initial)
        >>> for setup in generator:
        ...     print(setup[0].exchanges.root.action, app.compare_states(setup[0].initial))
        RL True
        PP False
    """
    for _run, _app in _find_runs(application, target).items():
        proc = checkmate.runtime.procedure.Procedure()
        _app.fill_procedure(proc)
        yield (proc, )

def _find_runs(application, target):
    """
        >>> import checkmate.sandbox
        >>> import sample_app.application
        >>> import checkmate.paths_finder
        >>> import checkmate.runtime.test_plan
        >>> import checkmate.runtime.pathfinder
        >>> runs = checkmate.paths_finder.RunCollection()
        >>> a = sample_app.application.TestData()

        >>> runs.build_trees_from_application(type(a))
        >>> ac_run = [r for r in runs if r.get_node(r.root)._tag.outgoing[0].code == 'AC'][0]
        >>> rl_run = [r for r in runs if r.get_node(r.root)._tag.outgoing[0].code == 'RL'][0]

        >>> box = checkmate.sandbox.Sandbox(a)
        >>> box([ac_run.get_node(ac_run.root)._tag, rl_run.get_node(rl_run.root)._tag,])
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
    runs = checkmate.paths_finder.RunCollection()
    runs.build_trees_from_application(type(application))
    used_runs = _next_run(application, target, runs, collections.OrderedDict())
    return used_runs

def _next_run(application, target, runs, used_runs):
    box = checkmate.sandbox.Sandbox(application)
    for _run in runs:
        if _run in used_runs:
            continue
        box([_run.get_node(_run.root)._tag])
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

def get_transition_from_pathfinder(application, initial, runs):
    """
        >>> import checkmate.runtime.pathfinder
        >>> import checkmate.test_data
        >>> import checkmate.sandbox
        >>> a = checkmate.test_data.App()
        >>> a.start()
        >>> initial_states = a.components['C1'].state_machine.transitions[2].initial + a.components['C3'].state_machine.transitions[2].initial
        >>> a.components['C3'].states[0].value
        'False'
        >>> runs = [[a.components['C1'].state_machine.transitions[0]], [a.components['C3'].state_machine.transitions[1]], [a.components['C1'].state_machine.transitions[2]]]
        >>> box = checkmate.sandbox.Sandbox(a)
        >>> transitions = checkmate.runtime.pathfinder.get_transition_from_pathfinder(a, initial_states, runs)
        >>> len(transitions)
        2
        >>> (transitions[0][0].incoming[0].factory().action, transitions[1][0].incoming[0].factory().action)
        ('AC', 'RL')
    """
    box = checkmate.sandbox.Sandbox(application)
    path = []
    for _run in runs:
        if box(_run) == False:
            continue
        if box.application.compare_states(initial):
            path.append(_run)
            break
        index = runs.index(_run)
        if index < len(runs)-1:
            new_runs = runs[:index] + runs[index+1:]
            tmp_path = get_transition_from_pathfinder(box.application, initial, new_runs)
            if tmp_path is not None and len(tmp_path) > 0:
                path.extend([_run] + tmp_path)
                break
    if len(path) > 0:
        return path

