
        >>> import checkmate.runs
        >>> import checkmate.sandbox
        >>> import checkmate.pathfinder
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.communication
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> runs = a.run_collection()
        >>> ac_run = [r for r in runs if r.root.incoming[0].code == 'PBAC'][0]
        >>> rl_run = [r for r in runs if r.root.incoming[0].code == 'PBRL'][0]

        >>> box = checkmate.sandbox.Sandbox(type(a))
        >>> box(ac_run.exchanges)
        True
        >>> box(rl_run.exchanges)
        True
        >>> runs = []
        >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime.communication.Communication)
        >>> for r in checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData):
        ...     runs.append(r[0])
        ...     

        >>> runs[0].root.outgoing[0].code
        'RE'
        >>> len(checkmate.pathfinder._find_runs(box.application, runs[0], rl_run))
        1
