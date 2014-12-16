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
    >>> runs = []
    >>> for run in checkmate.runtime.test_plan.TestProcedureFeaturesGenerator(sample_app.application.TestData):
    ...     runs.append(run[0])


Send 'AC' for append default 'R':
    >>> proc = [r.build_procedure(_r) for _r in runs if len(_r.root.incoming) > 0 and _r.root.incoming[0].code == 'PBAC'][0]
    >>> import checkmate.sandbox
    >>> saved = checkmate.sandbox.Sandbox(r.application)
    >>> proc(r)
    >>> final = [_f for _f in proc.final if _f.interface == sample_app.component.component_1_states.IAnotherState][0]
    >>> final.function #doctest: +ELLIPSIS
    <function AnotherState.__init__ at ...

    >>> validated_incoming = r.application.validated_incoming_list()
    >>> saved_final = [_f for _f in saved.application.state_list() if final.interface.providedBy(_f)]
    >>> saved_initial = [_s for _s in saved.application.state_list() if final.interface.providedBy(_s)]
    >>> res = final.factory(instance=saved_final[0], **final.resolve(saved_initial, validated_incoming))
    >>> res.R #doctest: +ELLIPSIS
    <sample_app.data_structure.ActionRequest object at ...
    >>> r.application.components['C1'].states[1].R #doctest: +ELLIPSIS
    <sample_app.data_structure.ActionRequest object at ...

Check the resulting final state compared to transition's final:
    >>> r.application.components['C1'].states[1] == res
    True

Result from compare_states():
    >>> final.match(r.application.state_list(), saved.application.state_list(), validated_incoming) #doctest: +ELLIPSIS
    <sample_app.component.component_1_states.AnotherState object at ...
    >>> r.application.compare_states(proc.final, saved.application.state_list())
    True
    >>> 
    >>> r.stop_test()
    >>>

