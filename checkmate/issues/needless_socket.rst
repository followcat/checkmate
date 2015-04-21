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
    >>> simulated_transition = r.application.components['C2'].engine.blocks[0]
    >>> o = c2_stub.simulate(simulated_transition)
    >>> c1_stub.validate(c1_stub.context.engine.blocks[1])
    True
    >>> c1_stub.validate(c1_stub.context.engine.blocks[1])
    False
    >>> r.stop_test()
