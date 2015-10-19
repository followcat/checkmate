The user transition lead to collected runs:

    >>> import checkmate.runs
    >>> import user_app.application
    >>> app = user_app.application.TestData()
    >>> app.start(False)
    >>> checkmate.runs.get_origin_exchanges(app) # doctest: +ELLIPSIS
    [<user_app.exchanges.ExchangeButton object at ...
    >>> len(checkmate.runs.get_origin_exchanges(app))
    3

