if the transition incoming comes like "AP(R1)", calling factory()
function without giving resolved_arguments will be ok.
    >>> import sample_app.application
    >>> a = sample_app.application.TestData()
    >>> t = a.components['C1'].engine.blocks[0]
    >>> t.incoming[0].factory().broadcast
    False
    >>> import checkmate._storage
    >>> module_dict = {
    ...     'states': [sample_app.component.component_1_states], 
    ...     'exchanges':[sample_app.exchanges]}
    >>> item = {'name': 'Toggle TestState tran01', 
    ...         'initial': [{'AnotherState': '__init__()'}], 
    ...         'outgoing': [{'ThirdAction': 'DA()'}], 
    ...         'incoming': [{'Action': 'AP(R1)'}], 
    ...         'final': [{'AnotherState': 'append(R1)'}]}
    >>> ts = checkmate._storage.TransitionStorage(item, module_dict)
    >>> t = ts.factory()
    >>> ex = t.incoming[0].factory()
    >>> ex.broadcast
    False
