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
    >>> runs[1].compare_initial(r.application)
    True
    >>> r.execute(runs[1])
    >>> t = c1.context.block_by_name("Append element ok tran01")
    >>> final_list = list(runs[1].final)
    >>> an_index = [_f.function for _f in final_list].index(
    ... sample_app.component.component_1_states.AnotherState.__init__)
    >>> ap = sample_app.exchanges.Action('AP')
    >>> revolved_args = final_list[an_index].resolve(exchanges=[ap],
    ...                     resolved_dict=t.resolve_dict)
    >>> fs = final_list[an_index].factory(
    ...         instance=r.application.components['C1'].states[1],
    ...         **revolved_args)
    >>> (fs.R.C.value, fs.R.P.value)
    ('AT1', 'NORM')
    >>> runs[1].compare_final(r.application)
    True
    >>> r.stop_test()
    >>>
