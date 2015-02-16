It is impossible to specify the final state by providing arguments 
(like __init__(R))
    >>> import checkmate.sandbox
    >>> import checkmate.runtime._pyzmq
    >>> import checkmate.runtime._runtime
    >>> import checkmate.runtime.test_plan
    >>> import sample_app.application
    >>> r = checkmate.runtime._runtime.Runtime(
    ...     sample_app.application.TestData, 
    ...     checkmate.runtime._pyzmq.Communication, threaded=True)
    >>> r.setup_environment(['C1'])
    >>> r.start_test()
    >>> c1 = r.runtime_components['C1']
    >>> test_module = checkmate.runtime.test_plan
    >>> gen = test_module.TestProcedureInitialGenerator(
    ...         sample_app.application.TestData)
    >>> runs = []
    >>> for run in gen:
    ...     run[0].application = r.application
    ...     runs.append(run[0])
    ... 
    >>> r.application.compare_states(runs[1].initial)
    True
    >>> saved_initial = \
    ...     checkmate.sandbox.Sandbox(type(r.application),
    ...         r.application)
    >>> r.execute(runs[1])
    >>> runs[1].final[0].function #doctest: +ELLIPSIS
    <function AnotherState.__init__ at ...
    >>> ap = sample_app.exchanges.Action('AP')
    >>> revolved_args = runs[1].final[0].resolve(exchanges=[ap])
    >>> fs = runs[1].final[0].factory(
    ...         instance=r.application.components['C1'].states[1],
    ...         **revolved_args)
    >>> (fs.R.C.value, fs.R.P.value)
    ('AT1', 'NORM')
    >>> r.application.compare_states(runs[1].final,
    ...     saved_initial.application.state_list())
    True
    >>> r.stop_test()
    >>>
