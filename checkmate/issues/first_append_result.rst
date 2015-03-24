This procedure shows that when the first State.append() call is made,
the resulting final state is the one that was expected by the transition
and the compare_states() done in Procedure is successful.

Setup:

    >>> import sample_app.application
    >>> import sample_app.component.component_1_states
    >>> import checkmate.runtime._pyzmq
    >>> import checkmate.runtime._runtime
    >>> import checkmate.runtime.test_plan
    >>> r = checkmate.runtime._runtime.Runtime(
    ...         sample_app.application.TestData,
    ...         checkmate.runtime._pyzmq.Communication,
    ...         threaded=True)
    >>> r.setup_environment(['C1'])
    >>> r.start_test()
    >>> c1 = r.runtime_components['C1']
    >>> c2 = r.runtime_components['C2']
    >>> c3 = r.runtime_components['C3']
    >>> user = r.runtime_components['USER']
    >>> runs = []
    >>> g = checkmate.runtime.test_plan.TestProcedureFeaturesGenerator
    >>> for run in g(sample_app.application.TestData):
    ...     runs.append(run[0])


Send 'AC' for append default 'R':

    >>> run = [_r for _r in runs if len(_r.root.incoming) > 0 and
    ...        _r.root.incoming[0].code == 'PBAC'][0]
    >>> import checkmate.sandbox
    >>> saved = checkmate.sandbox.Sandbox(type(r.application),
    ...             r.application)
    >>> r.execute([_r for _r in runs if len(_r.root.incoming) > 0 and
    ...            _r.root.incoming[0].code == 'PBAC'][0])
    >>> r.application.components['C1'].states[1].R #doctest: +ELLIPSIS
    <sample_app.data_structure.ActionRequest object at ...

Result from compare_states():

    >>> run.compare_final(r.application, saved.application)
    True
    >>> 
    >>> r.stop_test()
    >>>

