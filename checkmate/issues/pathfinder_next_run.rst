
        >>> import collections
        >>> import checkmate.sandbox
        >>> import checkmate.pathfinder
        >>> import checkmate.runtime.test_plan
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.communication
        >>> import sample_app.application
        >>> _c = sample_app.application.TestData
        >>> a = _c()
        >>> box = checkmate.sandbox.Sandbox(_c)
        >>> r = checkmate.runtime._runtime.Runtime(_c, checkmate.runtime.communication.Communication)
        >>> runs = []
        >>> for r in checkmate.runtime.test_plan.TestProcedureInitialGenerator(_c):
        ...     runs.append(r[0])

        >>> runs[0].root.outgoing[0].code
        'AC'
        >>> [_t.root.outgoing[0].code for _t in checkmate.pathfinder._next_run(box.application, runs[0], a.run_collection, collections.OrderedDict())]
        ['PBAC', 'PBRL', 'PBPP']

        >>> runs[3].root.outgoing[0].code
        'PP'
        >>> [_t.root.outgoing[0].code for _t in checkmate.pathfinder._next_run(box.application, runs[3], a.run_collection, collections.OrderedDict())]
        ['PBAC', 'PBRL']
