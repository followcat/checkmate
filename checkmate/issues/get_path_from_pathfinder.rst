
        >>> import checkmate.sandbox
        >>> import checkmate.pathfinder
        >>> import checkmate.runtime.test_plan
        >>> import sample_app.application
        >>> import sample_app.exchanges
        >>> import sample_app.runtime.test_procedure
        >>> _class = sample_app.application.TestData
        >>> box = checkmate.sandbox.Sandbox(_class)
        >>> app = box.application
        >>> ex1 = sample_app.exchanges.Action('AC')
        >>> ex1.origin_destination('C2', 'C1')
        >>> _t = box.application.components['C2'].get_blocks_by_output([ex1])
        >>> run = checkmate.runtime.test_plan.get_runs_from_transition(app, _t)[0]
        >>> box(run.exchanges)
        True
        >>> app.components['C3'].states[0].value
        True
        >>> run = sample_app.runtime.test_procedure.TestProcedureRun1Threaded(_class)
        >>> setup = checkmate.pathfinder._find_runs(app, run, run)
        >>> for _s in setup:
        ...     print(_s.root.incoming[0].code, _s.compare_initial(app))
        PBRL True
        PBPP False
