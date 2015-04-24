Setting the procedure.final from the sandbox does not work.
    >>> import checkmate.sandbox
    >>> import checkmate.runtime._pyzmq
    >>> import checkmate.runtime._runtime
    >>> import checkmate.runtime.test_plan
    >>> import checkmate.parser.yaml_visitor
    >>> import sample_app.application
    >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
    >>> r.setup_environment(['C1'])
    >>> r.start_test()
    >>> c1 = r.runtime_components['C1']
    >>> _application = sample_app.application.TestData()
    >>> components = list(_application.components.keys())
    >>> data = checkmate.tymata.visitor.data_from_files(_application)
    >>> run_list = checkmate.runtime.test_plan.get_runs_from_test(data, _application)
    >>> _run = run_list[0]
    >>> box = checkmate.sandbox.Sandbox(type(_application))
    >>> box(_run, itp_run=True)
    True
    >>> run = box.blocks
    >>> len(run.final)
    4
    >>> ff = [_f.function for _f in run.final]
    >>> sample_app.component.component_1_states.State.__init__ in ff
    True
    >>> sample_app.component.component_1_states.State.toggle in ff
    True
    >>> sample_app.component.component_1_states.State.append in ff
    True
    >>> run.compare_initial(r.application)
    True
    >>> r.execute(_run)
    >>> r.stop_test()
    >>> 
