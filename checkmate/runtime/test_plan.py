# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os.path

import checkmate.runs
import checkmate.sandbox
import checkmate.parser.yaml_visitor
import checkmate.partition_declarator
import checkmate.parser.feature_visitor


def get_runs_from_test(data, application):
    """
        >>> import checkmate.runtime.test_plan
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> data = checkmate.parser.yaml_visitor.data_from_files(a)
        >>> checkmate.runtime.test_plan.get_runs_from_test(
        ...     data, a) #doctest: +ELLIPSIS
        [<checkmate.runs.Run object at ...
    """

    runs = []
    components = list(application.components.keys())
    state_modules = []
    for name in components:
        state_modules.append(application.components[name].state_module)
    exchange_module = application.exchange_module

    for array_items in data:
        transition = checkmate.partition_declarator.make_transition(
                        array_items, [exchange_module], state_modules)
        gen_runs = checkmate.runs.get_runs_from_transition(application,
                        transition, itp_transition=True)
        runs.append(gen_runs[0])
    return runs

def TestProcedureInitialGenerator(application_class, transition_list=None):
    """
        >>> import time
        >>> import checkmate.runs
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> import sample_app.application
        >>> app = sample_app.application.TestData
        >>> com = checkmate.runtime._pyzmq.Communication
        >>> r = checkmate.runtime._runtime.Runtime(app, com, True)
        >>> r.setup_environment(['C1'])
        >>> r.start_test()
        >>> c1 = r.runtime_components['C1']
        >>> c2 = r.runtime_components['C2']
        >>> c3 = r.runtime_components['C3']
        >>> transition = c2.context.state_machine.transitions[0]
        >>> previous_run = checkmate.runs.get_runs_from_transition(
        ...                     r.application, transition)[0]
        >>> o = c2.simulate(transition) # doctest: +ELLIPSIS
        >>> time.sleep(1)
        >>> c1.context.states[0].value
        False
        >>> c3.context.states[0].value
        True
        >>> test_plan = checkmate.runtime.test_plan
        >>> run = [run[0] for run in
        ...        test_plan.TestProcedureInitialGenerator(app)][0]
        >>> run.compare_initial(r.application)
        False
        >>> r.execute(run, transform=True, previous_run=previous_run)
        >>> r.stop_test()

    """
    _application = application_class()
    data = checkmate.parser.yaml_visitor.data_from_files(_application)
    for _run in get_runs_from_test(data, _application):
        yield _run, _run.root.name


def TestProcedureFeaturesGenerator(application_class):
    """
        >>> import checkmate.sandbox
        >>> import checkmate.parser.feature_visitor
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> data = checkmate.parser.feature_visitor.data_from_files(a)
        >>> test_plan = checkmate.runtime.test_plan
        >>> run_list = test_plan.get_runs_from_test(data, a)
        >>> run_list.sort(key=lambda x:x.root.outgoing[0].code)
        >>> run_list[0].root.incoming[0].code
        'PBAC'
        >>> box = checkmate.sandbox.Sandbox(type(a), a,
        ...         run_list[0].walk())
        >>> c1_state = box.application.components['C1'].states[0]
        >>> c1_state.value == run_list[0].itp_run.root.initial[0].value
        True
        >>> run_list[0].compare_initial(box.application)
        True
        >>> box(run_list[0])
        True
        >>> len(run_list[0].initial)
        4

        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> app = sample_app.application.TestData
        >>> com = checkmate.runtime._pyzmq.Communication
        >>> r = checkmate.runtime._runtime.Runtime(app, com, True)
        >>> r.setup_environment(['C1'])
        >>> r.start_test()
        >>> c1 = r.runtime_components['C1']
        >>> c2 = r.runtime_components['C2']
        >>> c3 = r.runtime_components['C3']
        >>> runs = []
        >>> test_plan = checkmate.runtime.test_plan
        >>> runs = [run[0] for run in
        ...        test_plan.TestProcedureFeaturesGenerator(app)]
        >>> r.execute(runs[0])
        >>> r.stop_test()
    """
    _application = application_class()
    data = checkmate.parser.feature_visitor.data_from_files(_application)
    for _run in get_runs_from_test(data, _application):
        yield _run, _run.root.name
        

def TestProcedureRunsGenerator(application_class):
    """
        >>> import sample_app.application
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> runs = []
        >>> app = sample_app.application.TestData
        >>> test_plan = checkmate.runtime.test_plan
        >>> runs = [run[0] for run in
        ...        test_plan.TestProcedureRunsGenerator(app)]
        >>> runs[0].root.outgoing[0].code
        'PBAC'
        >>> runs[1].root.outgoing[0].code
        'PBAC'
        >>> runs[2].root.outgoing[0].code
        'PBRL'
        >>> runs[3].root.outgoing[0].code
        'PBPP'
        >>> com = checkmate.runtime._pyzmq.Communication
        >>> r = checkmate.runtime._runtime.Runtime(app, com, True)
        >>> r.setup_environment(['C2'])
        >>> r.start_test()
        >>> r.execute(runs[0], transform=False)
        >>> r.stop_test()
    """
    for _run in application_class().run_collection():
        yield _run, _run.root.name

