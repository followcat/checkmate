When an application has an empty run_collection, starting_run() method
is handling the case right:

    >>> import checkmate.application
    >>> import checkmate.runs
    >>> app = checkmate.application.Application()
    >>> run = app.starting_run()
    >>> checkmate.runs.followed_runs(app, run)
    []

Revert class attribute after test done
    >>> delattr(type(app), type(app)._run_collection_attribute)
