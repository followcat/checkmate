If the communication of exchange is not defined in runtime's
communication_list, then a new default communication instance
will be created in runtime for it during runtime_component setup.

    >>> import sample_app.application
    >>> import checkmate.runtime._runtime
    >>> import checkmate.runtime._pyzmq
    >>> ac = sample_app.application.TestData
    >>> cc = checkmate.runtime._pyzmq.Communication
    >>> r = checkmate.runtime._runtime.Runtime(ac, cc, True)
    >>> sample_app.exchanges.ExchangeButton.communication
    'interactive'
    >>> 'interactive' in r.communication_list
    False
    >>> r.setup_environment(['C1'])
    >>> 'interactive' in r.communication_list
    True
    >>> r.stop_test()

