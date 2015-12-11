if origin exchange is not from component's output, then exchange'origin
should be ''
    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> exchanges = app.origin_exchanges()
    >>> exchanges[0].origin, exchanges[0].destination
    ('', ['C2'])

