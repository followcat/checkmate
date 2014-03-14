import copy
import checkmate.runtime.test_plan


def get_path_from_pathfinder(application_class, application, target):
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
        >>> box = checkmate.sandbox.Sandbox(_class)
        >>> ex1 = sample_app.exchanges.AC()
        >>> ex1.origin_destination('C2', 'C1')
        >>> box.generate([ex1])
        >>> app = box.application
        >>> app.components['C3'].states[0].value
        'True'
        >>> checkmate.runtime.registry.global_registry.registerUtility(app, checkmate.application.IApplication)
        >>> proc = sample_app.runtime.test_procedure.TestProcedureRun1Threaded(_class)
        >>> generator = checkmate.runtime.pathfinder.get_path_from_pathfinder(_class, app, proc.initial)
        >>> for setup in generator:
        ...     print(setup[0].exchanges.root.action, setup[0].compare_states(setup[0].initial))
        RL True
        PP False
    """
    setup = []
    for proc in checkmate.runtime.test_plan.TestProcedureInitialGenerator(application_class):
        setup.append(proc)

    for proc in setup[2:]:
        yield proc

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
        >>> box = checkmate.sandbox.Sandbox(type(a), initial_application=a)
        >>> transitions = checkmate.runtime.pathfinder.get_transition_from_pathfinder(a, initial_states, runs)
        >>> len(transitions)
        2
        >>> (transitions[0][0].incoming[0].factory().action, transitions[1][0].incoming[0].factory().action)
        ('AC', 'RL')
    """
    box = checkmate.sandbox.Sandbox(type(application), initial_application=application)
    path = []
    for _run in runs:
        if box(_run) == False:
            continue
        if compare_states(box.application, initial):
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

def compare_states(application, target):
    """"""
    matching = 0
    for _target in target:
        for _component in list(application.components.values()):
            try:
                #Assume at most one state of component implements interface
                _state = [_s for _s in _component.states if _target.interface.providedBy(_s)].pop(0)
                if _state == _target.factory():
                    matching += 1
                    break
                else:
                    break
            except IndexError:
                continue
    return matching == len(target)

