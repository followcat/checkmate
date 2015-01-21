
        >>> import checkmate.runs
        >>> import checkmate.sandbox
        >>> import checkmate.pathfinder
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.communication
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> runs = a.run_collection
        >>> ac_run = [r for r in runs if r.root.outgoing[0].code == 'PBAC'][0]
        >>> rl_run = [r for r in runs if r.root.outgoing[0].code == 'PBRL'][0]

        >>> box = checkmate.sandbox.Sandbox(a)
        >>> box(ac_run)
        True
        >>> box(rl_run)
        True
        >>> proc = []
        >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime.communication.Communication)
        >>> for p in checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData):
        ...     proc.append(r.build_procedure(p[0]))
        ...     

        >>> proc[0].transitions.root.outgoing[0].code
        'AC'
        >>> len(checkmate.pathfinder._find_runs(box.application, proc[0].initial))
        3
