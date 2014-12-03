
        >>> import checkmate.runs
        >>> import checkmate.sandbox
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.registry
        >>> import checkmate.runtime.procedure
        >>> import checkmate.runtime.communication
        >>> import sample_app.application
        >>> import sample_app.exchanges
        >>> import sample_app.runtime.test_procedure
        >>> cc = checkmate.runtime.communication.Communication
        >>> _class = sample_app.application.TestData
        >>> runs = checkmate.runs.RunCollection()
        >>> runs.build_trees_from_application(_class())
        >>> r = checkmate.runtime._runtime.Runtime(_class, cc)
        >>> box = checkmate.sandbox.Sandbox(_class())
        >>> ex1 = sample_app.exchanges.Action('AC')
        >>> ex1.origin_destination('C2', 'C1')
        >>> _t = box.application.components['C2'].get_transition_by_output([ex1])
        >>> transitions = box.generate([ex1], checkmate._tree.Tree(_t, []))
        >>> app = box.application
        >>> app.components['C3'].states[0].value
        'True'
        >>> registry = checkmate.runtime.registry.RuntimeGlobalRegistry()
        >>> registry.registerUtility(app, checkmate.application.IApplication)
        >>> proc = sample_app.runtime.test_procedure.TestProcedureRun1Threaded(_class)
        >>> setup = checkmate.runtime.procedure.get_path_from_pathfinder(app, proc.initial)
        >>> for _s in setup:
        ...     print(_s.transitions.root.outgoing[0].code, app.compare_states(_s.initial))
        PBRL True
        PBPP False
