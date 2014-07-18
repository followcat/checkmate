This procedure shows that when the first State.append() call is made,
the resulting final state is the one that was expected by the transition
and the compare_states() done in Procedure is successful.

Setup:
    >>> import sample_app.application
    >>> import sample_app.component.component_1_states
    >>> import checkmate.runtime._pyzmq
    >>> import checkmate.runtime._runtime
    >>> import checkmate.runtime.test_plan
    >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
    >>> r.setup_environment(['C1'])
    >>> r.start_test()
    >>> c1 = r.runtime_components['C1']
    >>> c2 = r.runtime_components['C2']
    >>> c3 = r.runtime_components['C3']
    >>> user = r.runtime_components['USER']
    >>> procedures = []
    >>> for p in checkmate.runtime.test_plan.TestProcedureFeaturesGenerator(sample_app.application.TestData):
    ...     procedures.append(p[0])


Send 'AC' for append default 'R':
    >>> proc = [_p for _p in procedures if len(_p.transitions.root.incoming) > 0 and _p.transitions.root.incoming[0].code == 'PBAC'][0]
    >>> import checkmate.sandbox
    >>> saved = checkmate.sandbox.Sandbox(r.application)
    >>> user.simulate(proc.transitions.root) #doctest: +ELLIPSIS
    [<sample_app.exchanges.Action object at ...
    >>> len(c2.context.validation_list) == 2
    True
    >>> final = [_f for _f in proc.final if _f.interface == sample_app.component.component_1_states.IAnotherState][0]
    >>> final.function #doctest: +ELLIPSIS
    <function State.append at ...

    >>> res = final.factory([saved.application.state_list()[2]])
    >>> res.value
    [{'R': ['AT1', 'NORM']}]
    >>> r.application.state_list()[2].value
    [{'R': ['AT1', 'NORM']}]

Check the resulting final state compared to transition's final:
    >>> r.application.state_list()[2] == res
    True

Result from compare_states():
    >>> len(final.match(r.application.state_list(), saved.application.state_list()))
    2
    >>> r.application.compare_states(proc.final, saved.application.state_list())
    True

