Using compare_state() with transition's final InternalStorage as target does not work.
    >>> import checkmate.sandbox
    >>> import checkmate.runtime._pyzmq
    >>> import checkmate.runtime._runtime
    >>> import checkmate.runtime.test_plan
    >>> import sample_app.application
    >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
    >>> r.setup_environment(['C1'])
    >>> r.start_test()
    >>> _application = sample_app.application.TestData()
    >>> components = list(_application.components.keys())
    >>> run_list = checkmate.runtime.test_plan.get_runs_from_test(_application)
    >>> _run = run_list[1]
    >>> _run.final[0].function #doctest: +ELLIPSIS
    <function AnotherState.__init__ at ...
    >>> _run.nodes[0].compare_initial(r.application)
    True

This is a class method not an instance method.
Calling it would require to pass an instance as first argument.
    >>> _run.nodes[0].final[0].function  #doctest: +ELLIPSIS
    <function State.append at ...

This fails during the Procedure's compare_states(self.final), as the InternalStorage factory
only pass args and kwargs but not an instance.
This lead to a strange error ('str' object has no attribute 'value') showing that first argument
is used as if it was an instance.
    >>> r.execute(_run) #doctest: +IGNORE_EXCEPTION_DETAIL
    >>> r.stop_test()
    >>> 

