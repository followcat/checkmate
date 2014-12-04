The Runs Collection should return 4 runs, should be two runs begin from PBAC.
    >>> import checkmate.runs
    >>> import sample_app.application
    >>> a = sample_app.application.TestData()
    >>> src = checkmate.runs.SandboxRunCollection(a)
    >>> src.get_runs()
    >>> len(src)
    4
    >>> src[0].nodes[0].nodes[0].root.incoming[0].code
    'AC'
    >>> src[1].nodes[0].nodes[0].root.incoming[0].code
    'AC'

