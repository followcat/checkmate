It is impossible to specify the final state by providing arguments (like __init__(R))
    >>> import checkmate.runtime._pyzmq
    >>> import checkmate.runtime._runtime
    >>> import checkmate.runtime.test_plan
    >>> import sample_app.application
    >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
    >>> r.setup_environment(['C1'])
    >>> r.start_test()
    >>> c1 = r.runtime_components['C1']
    >>> c1.context.states[0].value
    'True'
    >>> c1.context.states[1].value
    >>> gen = checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData)
    >>> procedures = []
    >>> for p in gen:
    ...     p[0].application = r.application
    ...     procedures.append(p[0])
    ... 
    >>> proc = procedures[1]
    >>> r.application.compare_states(proc.initial)
    True
    >>> proc(r)
    >>> proc.final[0].function
    <class 'sample_app.component.component_1_states.AnotherState'>
    >>> proc.final[0].factory().value
    'R'
    >>> r.application.compare_states(proc.final)
    True
    >>> r.stop_test()
    >>>
