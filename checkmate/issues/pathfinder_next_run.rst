
        >>> import collections
        >>> import checkmate.sandbox
        >>> import checkmate.pathfinder
        >>> import checkmate.runtime.test_plan
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> box = checkmate.sandbox.Sandbox(a)
        >>> proc = []
        >>> for p in checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData):
        ...     proc.append(p)

        >>> proc[0][0].transitions.root.outgoing[0].code
        'AC'
        >>> [_t.root.outgoing[0].code for _t in checkmate.pathfinder._next_run(box.application, proc[0][0].initial, a.origin_transitions, collections.OrderedDict())]
        ['PBAC', 'PBRL', 'PBPP']

        >>> proc[3][0].transitions.root.outgoing[0].code
        'PP'
        >>> [_t.root.outgoing[0].code for _t in checkmate.pathfinder._next_run(box.application, proc[3][0].initial, a.origin_transitions, collections.OrderedDict())]
        ['PBAC', 'PBRL']
