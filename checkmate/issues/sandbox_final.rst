Setting the procedure.final from the sandbox does not work.
    >>> import checkmate.sandbox
    >>> import checkmate.runtime._pyzmq
    >>> import checkmate.runtime._runtime
    >>> import checkmate.runtime.test_plan
    >>> import sample_app.application
    >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
     >>> r.setup_environment(['C1'])
    >>> r.start_test()
    >>> c1 = r.runtime_components['C1']
    >>> _application = sample_app.application.TestData()
    >>> components = list(_application.components.keys())
    >>> transition_list = checkmate.runtime.test_plan.get_transitions_from_test(_application)
    >>> _transition = transition_list[0]
    >>> box = checkmate.sandbox.Sandbox(_application, [_transition])
    >>> box(_transition, foreign_transitions=True)
    True
    >>> proc = checkmate.runtime.test_plan.build_procedure(box,  box)
    >>> len(proc.final)
    3
    >>> proc.final[0].function
    <class 'sample_app.component.component_1_states.State'>
    >>> proc.final[1].function #doctest: +ELLIPSIS
    <function State.toggle at ...
    >>> proc.final[2].function #doctest: +ELLIPSIS
    <function State.append at ...
    >>> r.application.compare_states(proc.initial)
    True
    >>> proc(r)
    Traceback (most recent call last):
    ...
    TypeError: toggle() missing 1 required positional argument: 'self'
    >>> r.stop_test()
    >>> 
