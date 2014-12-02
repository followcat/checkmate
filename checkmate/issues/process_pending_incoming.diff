A component will wait for return code by storing pending incoming:
    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> c2 = app.components['C2']
    >>> c2.process([sample_app.exchanges.ExchangeButton('PBAC')]) #doctest: +ELLIPSIS
    [<sample_app.exchanges.Action object at ...

The exchange that requires a return will be stored:
    >>> c2.expected_return_code.value
    'AC'
    >>> c2.expected_return_code.return_type
    <class 'sample_app.exchanges.ActionCode'>

If other exchanges are coming, they will not be processed.
They will be queued.
    >>> c2.process([sample_app.exchanges.ExchangeButton('PBAC')])
    []

After reception of the return code, the component will process
pending incoming exchanges:
    >>> c2.process([sample_app.exchanges.ActionCode(True)]) #doctest: +ELLIPSIS
    [<sample_app.exchanges.Action object at ...

