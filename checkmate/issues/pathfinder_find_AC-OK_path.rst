After execute run 'PBRL', components' state is State: Flase, Acknowledge: False, then run 'PBAC-AC-OK', path finder can find two path:['PBAC-AC-ER', 'PBRL', 'PBPP'] or ['PBPP'].
        >>> import sample_app.application
        >>> import checkmate.pathfinder
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime._pyzmq
        >>> ac = sample_app.application.TestData
        >>> cc = checkmate.runtime._pyzmq.Communication
        >>> r = checkmate.runtime._runtime.Runtime(ac, cc, True)
        >>> r.setup_environment(['C1'])
        >>> r.start_test()
        >>> runs = r.application.run_collection()
        >>> r.execute(runs[1], transform=True)
        >>> path_list = checkmate.pathfinder._find_runs(r.application,
        ...                 runs[0], runs[1])
        >>> [o.code for o in path_list[0].root.outgoing]
        ['PP']
        >>> r.stop_test()
