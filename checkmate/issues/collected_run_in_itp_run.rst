When getting a run from ITP, it is required to reference to a run in
application's run_collection in order to find a path:

    >>> import itertools
    >>> import sample_app.application
    >>> import checkmate.runtime.test_plan
    >>> app = sample_app.application.TestData()

    >>> gen = checkmate.runtime.test_plan.TestProcedureInitialGenerator
    >>> run_name = [_r for _r in itertools.islice(gen(type(app)), 1)][0]
    >>> run_name[0] in app.run_collection()
    False
    >>> run_name[0].collected_run in app.run_collection()
    True
