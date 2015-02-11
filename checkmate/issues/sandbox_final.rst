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
    >>> run_list = checkmate.runtime.test_plan.get_runs_from_test(_application)
    >>> _run = run_list[0]
    >>> box = checkmate.sandbox.Sandbox(_application, [_run.root])
    >>> box(_run, itp_run=True)
    True
    >>> run = box.transitions
    >>> len(run.final)
    3
    >>> run.final[0].function #doctest: +ELLIPSIS
    <function State.__init__ at ...
    >>> run.final[1].function #doctest: +ELLIPSIS
    <function State.toggle at ...
    >>> run.final[2].function #doctest: +ELLIPSIS
    <function State.append at ...
    >>> r.application.compare_states(run.initial)
    True
    >>> r.execute(_run)
    >>> r.stop_test()
    >>> 
