This comparison is taking the length of the target into account.
If a matching state is twice in the target, the comparison should
still be ok.

    >>> import checkmate.runs
    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> c1 = app.components['C1']
    >>> c1.states[0].value
    True
    >>> t = c1.engine.blocks[0]
    >>> t.initial[0].value
    True
    >>> inc = t.incoming[0]
    >>> ex = inc.factory(**inc.resolve())
    >>> run = checkmate.runs.Run(t, exchanges=[ex])
    >>> run.compare_initial(app)
    True
    >>> target = t.initial + t.initial
    >>> run.compare_initial(app)
    True
