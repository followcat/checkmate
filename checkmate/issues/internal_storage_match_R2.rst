This is checking that an 'AP(R2)' Action matches 'AP(R)' filter:

    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> import sample_app.exchanges
    >>> app_class = sample_app.application.TestData
    >>> r2 = app_class.data_value['ActionRequest']['R2']
    >>> ap = sample_app.exchanges.Action('AP', R=r2)
    >>> ap.R.C.value
    'AT2'
    >>> app.start()
    >>> c1 = app.components['C1']
    >>> i = c1.state_machine.transitions[1].incoming[0]
    >>> i.match([ap]) #doctest: +ELLIPSIS
    <sample_app.exchanges.Action object at ...
