import os.path

import checkmate.runs
import checkmate.sandbox
import checkmate.runtime.procedure
import checkmate.parser.yaml_visitor
import checkmate.partition_declarator
import checkmate.parser.feature_visitor


def build_procedure(sandbox, transition=None):
    proc = checkmate.runtime.procedure.Procedure()
    sandbox.fill_procedure(proc)
    if transition is not None:
        #force checking final from transition if given
        proc.final = transition.final
    return proc

def get_runs_from_test(application):
    """
        >>> import checkmate.runtime.test_plan
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> checkmate.runtime.test_plan.get_runs_from_test(a) #doctest: +ELLIPSIS 
        [<checkmate.runs.Run object at ...
    """

    exchange_module = application.exchange_module
    state_modules = []
    for name in list(application.components.keys()):
            state_modules.append(application.components[name].state_module)
    path = os.path.dirname(application.exchange_definition_file)
    array_list = []
    try:
        with open(os.sep.join([path, "itp.yaml"]), 'r') as _file:
            matrix = _file.read()
    except FileNotFoundError:
        return []
    _output = checkmate.parser.yaml_visitor.call_visitor(matrix)
    for data in _output['transitions']:
        array_list.append(data)
    runs = []
    for array_items in array_list:
        run = checkmate.runs.Run(checkmate.partition_declarator.make_transition(array_items, [exchange_module], state_modules))
        runs.append(run)
    return runs

def TestProcedureInitialGenerator(application_class, transition_list=None):
    """
        >>> import time
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> import sample_app.application
        >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
        >>> r.setup_environment(['C1'])
        >>> r.start_test()
        >>> c1 = r.runtime_components['C1']
        >>> c2 = r.runtime_components['C2']
        >>> c3 = r.runtime_components['C3']
        >>> simulated_transition = c2.context.state_machine.transitions[0]
        >>> o = c2.simulate(simulated_transition) # doctest: +ELLIPSIS
        >>> time.sleep(1)
        >>> c1.context.states[0].value
        'False'
        >>> c3.context.states[0].value
        'True'
        >>> gen = checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData)
        >>> procedures = []
        >>> for p in gen:
        ...     p[0].application = r.application
        ...     procedures.append(p[0])

        >>> proc = procedures[0]
        >>> r.application.compare_states(proc.initial)
        False
        >>> proc(r)
        >>> r.stop_test()

    """
    _application = application_class()
    components = list(_application.components.keys())
    state_modules = []
    for name in components:
        state_modules.append(_application.components[name].state_module)
    run_list = get_runs_from_test(_application)

    for _run in run_list:
        box = checkmate.sandbox.Sandbox(_application, [_run.root])
        box(_run.root, foreign_transitions=True)
        yield build_procedure(box, _run.root), box.transitions.root.owner, box.transitions.root.outgoing[0].code

def TestProcedureFeaturesGenerator(application_class):
    """
        >>> import checkmate.sandbox
        >>> import checkmate.parser.feature_visitor
        >>> import sample_app.application
        >>> _application = sample_app.application.TestData()
        >>> components = list(_application.components.keys())
        >>> state_modules = []
        >>> for name in components:
        ...         state_modules.append(_application.components[name].state_module)
        >>> transition_list = checkmate.parser.feature_visitor.get_transitions_from_features(_application.exchange_module, state_modules)
        >>> transition_list.sort(key=lambda x:x.incoming[0].code)
        >>> transition_list[0].incoming[0].code
        'AC'
        >>> box = checkmate.sandbox.Sandbox(_application, [transition_list[0]])
        >>> box.application.components['C1'].states[0].value == transition_list[0].initial[0].values[0]
        True
        >>> box.application.compare_states(transition_list[0].initial)
        True
        >>> box(transition_list[0], foreign_transitions=True)
        True
        >>> box.update_required_states(box.transitions)
        >>> len(box.initial)
        3

        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
        >>> r.setup_environment(['C1'])
        >>> r.start_test()
        >>> c1 = r.runtime_components['C1']
        >>> c2 = r.runtime_components['C2']
        >>> c3 = r.runtime_components['C3']
        >>> procedures = []
        >>> for p in checkmate.runtime.test_plan.TestProcedureFeaturesGenerator(sample_app.application.TestData):
        ...     procedures.append(p[0])
        >>> proc = procedures[0]
        >>> proc(r)
        >>> r.stop_test()
    """
    _application = application_class()
    components = list(_application.components.keys())
    state_modules = []
    for name in components:
        state_modules.append(_application.components[name].state_module)
    transition_list = checkmate.parser.feature_visitor.get_transitions_from_features(_application.exchange_module, state_modules, path=_application.feature_definition_path)

    for _transition in transition_list:
        box = checkmate.sandbox.Sandbox(_application, [_transition])
        box(_transition, foreign_transitions=True)
        yield build_procedure(box, _transition), box.transitions.root.owner, box.transitions.root.outgoing[0].code

def TestProcedureRunsGenerator(application_class):
    """
        >>> import sample_app.application
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> procedures = []
        >>> for p in checkmate.runtime.test_plan.TestProcedureRunsGenerator(sample_app.application.TestData):
        ...     procedures.append(p[0])
        >>> procedures[0].transitions.root.outgoing[0].code
        'PBAC'
        >>> procedures[1].transitions.root.outgoing[0].code
        'PBAC'
        >>> procedures[2].transitions.root.outgoing[0].code
        'PBRL'
        >>> procedures[3].transitions.root.outgoing[0].code
        'PBPP'
        >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
        >>> r.setup_environment(['C2'])
        >>> r.start_test()
        >>> procedures[0](r)
        >>> r.stop_test()
    """

    _application = application_class()
    runs = checkmate.runs.RunCollection()
    runs.get_runs_from_application(application_class()) 
    for _run in runs:
        box = checkmate.sandbox.Sandbox(_application, _run.walk())
        box(_run.root, foreign_transitions=True) 
        yield build_procedure(box), box.transitions.root.owner, box.transitions.root.outgoing[0].code

