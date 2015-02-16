
        >>> import checkmate.runs
        >>> import checkmate.sandbox
        >>> import checkmate.pathfinder
        >>> import sample_app.application
        >>> import sample_app.exchanges
        >>> import sample_app.runtime.test_procedure
        >>> _class = sample_app.application.TestData
        >>> box = checkmate.sandbox.Sandbox(_class)
        >>> app = box.application
        >>> ex1 = sample_app.exchanges.Action('AC')
        >>> ex1.origin_destination('C2', 'C1')
        >>> _t = box.application.components['C2'].get_transition_by_output([ex1])
        >>> run = checkmate.runs.get_runs_from_transition(app, _t)[0]
        >>> box(run)
        True
        >>> app.components['C3'].states[0].value
        'True'
        >>> run = sample_app.runtime.test_procedure.TestProcedureRun1Threaded(_class)
        >>> setup = checkmate.pathfinder._find_runs(app, run.initial)
        >>> for _s in setup:
        ...     print(_s.root.outgoing[0].code, app.compare_states(_s.initial))
        PBRL True
        PBPP False
