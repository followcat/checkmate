
        >>> import collections
        >>> import checkmate.sandbox
        >>> import checkmate.pathfinder
        >>> import checkmate.runtime.test_plan
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.communication
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> box = checkmate.sandbox.Sandbox(a)
        >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime.communication.Communication)
        >>> runs = []
        >>> for r in checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData):
        ...     runs.append(r[0])

        >>> runs[0].root.outgoing[0].code
        'AC'
        >>> [_t.root.outgoing[0].code for _t in checkmate.pathfinder._next_run(box.application, runs[0].initial, a.run_collection, collections.OrderedDict())]
        ['PBAC', 'PBRL', 'PBPP']

        >>> runs[3].root.outgoing[0].code
        'PP'
        >>> [_t.root.outgoing[0].code for _t in checkmate.pathfinder._next_run(box.application, runs[3].initial, a.run_collection, collections.OrderedDict())]
        ['PBAC', 'PBRL']
