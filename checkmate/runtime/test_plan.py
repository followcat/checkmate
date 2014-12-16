import os.path

import checkmate.runs
import checkmate.sandbox
import checkmate.runtime.procedure
import checkmate.parser.yaml_visitor
import checkmate.partition_declarator
import checkmate.parser.feature_visitor


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
        >>> runs = []
        >>> for run in gen:
        ...     run[0].application = r.application
        ...     runs.append(run[0])

        >>> proc = r.build_procedure(runs[0])
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

    for _run in get_runs_from_test(_application):
        yield _run, _run.root.name


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
        >>> run_list = checkmate.parser.feature_visitor.get_runs_from_features(_application.exchange_module, state_modules)
        >>> run_list.sort(key=lambda x:x.root.incoming[0].code)
        >>> run_list[0].root.incoming[0].code
        'AC'
        >>> box = checkmate.sandbox.Sandbox(_application, [run_list[0].root])
        >>> box.application.components['C1'].states[0].value == run_list[0].root.initial[0].values[0]
        True
        >>> box.application.compare_states(run_list[0].root.initial)
        True
        >>> box(run_list[0].root, foreign_transitions=True)
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
        >>> runs = []
        >>> for run in checkmate.runtime.test_plan.TestProcedureFeaturesGenerator(sample_app.application.TestData):
        ...     runs.append(run[0])
        >>> proc = r.build_procedure(runs[0])
        >>> proc(r)
        >>> r.stop_test()
    """
    _application = application_class()
    components = list(_application.components.keys())
    state_modules = []
    for name in components:
        state_modules.append(_application.components[name].state_module)
    run_list = checkmate.parser.feature_visitor.get_runs_from_features(_application.exchange_module, state_modules, path=_application.feature_definition_path)

    for _run in run_list:
        yield _run, _run.root.name
        

def TestProcedureRunsGenerator(application_class):
    """
        >>> import sample_app.application
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> runs = []
        >>> for run in checkmate.runtime.test_plan.TestProcedureRunsGenerator(sample_app.application.TestData):
        ...     runs.append(run[0])
        >>> runs[0].root.outgoing[0].code
        'PBAC'
        >>> runs[1].root.outgoing[0].code
        'PBAC'
        >>> runs[2].root.outgoing[0].code
        'PBRL'
        >>> runs[3].root.outgoing[0].code
        'PBPP'
        >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
        >>> r.setup_environment(['C2'])
        >>> r.start_test()
        >>> proc = r.build_procedure(runs[0])
        >>> proc(r)
        >>> r.stop_test()
    """

    _application = application_class()
    runs = checkmate.runs.RunCollection()
    runs.get_runs_from_application(application_class())
    for _run in runs:
        yield _run, _run.root.name
