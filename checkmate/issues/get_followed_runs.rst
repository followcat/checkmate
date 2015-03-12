    >>> import checkmate.runs
    >>> import checkmate.sandbox
    >>> import sample_app.application
    >>> box = checkmate.sandbox.Sandbox(sample_app.application.TestData)
    >>> app = box.application
    >>> runs  = app.origin_runs
    >>> runs[0].compare_initial(app)
    True
    >>> box(runs[0])
    True
    >>> fun = checkmate.runs.get_followed_runs_from_application
    >>> fun(app, runs[0]) #doctest: +ELLIPSIS
    [<checkmate.runs.Run object at ...
    >>> app.matrix
    matrix([[0, 0, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]])
    >>> box(runs[2])
    True
    >>> fun(app, runs[2]) #doctest: +ELLIPSIS
    [<checkmate.runs.Run object at ...
    >>> app.matrix
    matrix([[0, 0, 1, 0],
            [0, 0, 0, 0],
            [0, 1, 0, 1],
            [0, 0, 0, 0]])
    >>> box(runs[1])
    True
    >>> fun(app, runs[1]) #doctest: +ELLIPSIS
    [<checkmate.runs.Run object at ...
    >>> app.matrix
    matrix([[0, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 0, 0]])
    >>> box(runs[2])
    True
    >>> box(runs[3])
    True
    >>> fun(app, runs[3]) #doctest: +ELLIPSIS
    [<checkmate.runs.Run object at ...
    >>> app.matrix
    matrix([[0, 0, 1, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, 0, 0]])

