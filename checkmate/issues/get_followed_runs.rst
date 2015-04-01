    >>> import checkmate.runs
    >>> import checkmate.sandbox
    >>> import sample_app.application
    >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData)
    >>> app = box.application
    >>> app.define_exchange()
    >>> runs  = app.run_collection()
    >>> runs[0].compare_initial(app)
    True
    >>> box(runs[0])
    True
    >>> r0_fr = checkmate.runs.followed_runs(app, runs[0])
    >>> app._matrix
    matrix([[0, 0, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]])
    >>> runs[2] in r0_fr
    True
    >>> box(runs[2])
    True
    >>> r2_fr = checkmate.runs.followed_runs(app, runs[2])
    >>> app._matrix
    matrix([[0, 0, 1, 0],
            [0, 0, 0, 0],
            [0, 1, 0, 1],
            [0, 0, 0, 0]])
    >>> runs[1] in r2_fr, runs[3] in r2_fr
    (True, True)
    >>> box(runs[1])
    True
    >>> r1_fr = checkmate.runs.followed_runs(app, runs[1])
    >>> app._matrix
    matrix([[0, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 0, 0]])
    >>> runs[2] in r1_fr
    True
    >>> box(runs[2])
    True
    >>> box(runs[3])
    True
    >>> r3_fr = checkmate.runs.followed_runs(app, runs[3])
    >>> app._matrix
    matrix([[0, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, 0, 0]])
    >>> runs[0] in r3_fr
    True

