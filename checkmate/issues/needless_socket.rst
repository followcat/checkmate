Should not have same socket from C2stub to C1stub which is_server = False, is_broadcast = True.
    >>> import checkmate.runtime._pyzmq
    >>> import checkmate.runtime._runtime
    >>> import sample_app.application
    >>> a = sample_app.application.TestData
    >>> c = checkmate.runtime._pyzmq.Communication
    >>> r = checkmate.runtime._runtime.Runtime(a, c, True)
    >>> r.setup_environment(['C3'])
    >>> r.start_test()
    >>> c2_stub = r.runtime_components['C2']
    >>> c1_stub = r.runtime_components['C1']
    >>> inc = c2_stub.context.engine.blocks[0].incoming[0]
    >>> exchange = inc.factory(**inc.resolve())
    >>> exchange.origin_destination('', ['C2'])
    >>> simulated_exchanges = [exchange]
    >>> o = c2_stub.simulate(simulated_exchanges)
    >>> ap = sample_app.exchanges.Action('AP')
    >>> items = ((ap,), tuple(c1_stub.context.states))
    >>> c1_stub.validate(items)
    True
    >>> c1_stub.validate(items)
    False
    >>> r.stop_test()
