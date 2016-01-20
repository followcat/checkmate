# This code is part of the checkmate project.
# Copyright (C) 2013-2016 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import os.path

import checkmate.runs
import checkmate.sandbox
import checkmate.tymata.visitor
import checkmate.tymata.transition
import checkmate.partition_declarator
import checkmate.parser.feature_visitor


@checkmate.fix_issue('checkmate/issues/collected_run_in_itp_run.rst')
def get_runs_from_transition(application, transition, itp_transition=False):
    runs = []
    exchanges = []
    _class = type(application)
    box = checkmate.sandbox.Sandbox(_class, application, [transition])
    _incoming = transition.generic_incoming(box.application.state_list())
    origin = ''
    destination = []
    for _c in box.application.components.values():
        if _c.get_blocks_by_output(_incoming) is not None:
            origin = _c.name
        if len(_c.get_blocks_by_input(_incoming)) > 0:
            if _c.name not in destination:
                destination.append(_c.name)
    for _exchange in _incoming: 
        _exchange.origin_destination(origin, destination)
        exchanges.append(_exchange)
    assert box(exchanges)
    _run = box.blocks
    initial = checkmate.sandbox.Sandbox(_class, application, [transition])
    if itp_transition:
        _run.itp_final = transition.final
        _run._collected_box = initial
    runs.append(_run)
    return runs


def get_runs_from_test(data, application):
    """
        >>> import checkmate.runtime.test_plan
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> data = checkmate.tymata.visitor.data_from_files(a)
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
        transition = checkmate.tymata.transition.make_transition(
                        array_items, [exchange_module], state_modules)
        gen_runs = get_runs_from_transition(application,
                        transition, itp_transition=True)
        runs.append(gen_runs[0])
    return runs

def TestProcedureInitialGenerator(application_class, transition_list=None):
    """
        >>> import time
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
        >>> transition = c2.context.engine.blocks[0]
        >>> previous_run = get_runs_from_transition(
        ...                     r.application, transition)[0]
        >>> inc = transition.incoming[0]
        >>> exchange = inc.factory(**inc.resolve())
        >>> exchange.origin_destination('', ['C2'])
        >>> simulated_exchanges = [exchange]

        >>> o = c2.simulate(simulated_exchanges)
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
    data = checkmate.tymata.visitor.data_from_files(_application)
    for _run in get_runs_from_test(data, _application):
        yield _run, _run.root.name


def TestProcedureFeaturesGenerator(application_class):
    """
        >>> import checkmate.sandbox
        >>> import checkmate.runtime.test_plan
        >>> import checkmate.parser.feature_visitor
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> data = checkmate.parser.feature_visitor.data_from_files(a)
        >>> test_plan = checkmate.runtime.test_plan
        >>> run_list = test_plan.get_runs_from_test(data, a)
        >>> run_list.sort(key=lambda x:x.root.incoming[0].code)
        >>> run_list[1].root.incoming[0].code
        'AC'
        >>> box = checkmate.sandbox.Sandbox(type(a), a,
        ...         run_list[1].walk())
        >>> run_list[1].compare_initial(box.application)
        True
        >>> box(run_list[1].exchanges)
        True
        >>> len(run_list[1].initial)
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
        >>> func = [_f for _f in
        ...        test_plan.TestProcedureRunsGenerator(app)][0]
        >>> runs = [_r for _r in func(app())]
        >>> runs[0].root.incoming[0].code
        'PBAC'
        >>> runs[1].root.incoming[0].code
        'PBRL'
        >>> runs[2].root.incoming[0].code
        'PBAC'
        >>> runs[3].root.incoming[0].code
        'PBPP'
        >>> com = checkmate.runtime._pyzmq.Communication
        >>> r = checkmate.runtime._runtime.Runtime(app, com, True)
        >>> r.setup_environment(['C2'])
        >>> r.start_test()
        >>> r.execute(runs[0], transform=False)
        >>> r.stop_test()
    """
    yield checkmate.runs.origin_runs_generator

