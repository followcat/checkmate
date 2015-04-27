new a transition with initial like "__init__(R2)" then, get initial
factory() to return a state with R=R2, ('AT2','HIGH')
    >>> import sample_app.application
    >>> a = sample_app.application.TestData()
    >>> import checkmate.tymata.transition
    >>> c1_states = sample_app.component.component_1_states
    >>> module_dict = {'states': [c1_states],
    ...                'exchanges':[sample_app.exchanges]}
    >>> item = {'name': 'Toggle TestState tran01',
    ...         'initial':[{'AnotherState':'AnotherState1(R)'}],
    ...         'final': [{'AnotherState': 'pop(R)'}],
    ...         'incoming': [{'Action': 'PP(R)'}],
    ...         'outgoing': [{"Pause":"PA()"}]}
    >>> ts = checkmate.tymata.transition.TransitionStorage(item, module_dict)
    >>> t = ts.factory()
    >>> init_1 = t.initial[0].factory(**t.initial[0].resolve())
    >>> init_1.partition_attribute
    ('R',)
    >>> init_1.R
    >>> item = {'name': 'Toggle TestState tran01',
    ...         'initial':[{'AnotherState':'AnotherState1(R2)'}],
    ...         'final': [{'AnotherState': 'pop(R2)'}],
    ...         'incoming': [{'Action': 'PP(R2)'}],
    ...         'outgoing': [{"Pause":"PA()"}]}
    >>> ts = checkmate.tymata.transition.TransitionStorage(item, module_dict)
    >>> t = ts.factory()
    >>> init_1 = t.initial[0].factory(**t.initial[0].resolve())
    >>> init_1.partition_attribute
    ('R',)
    >>> init_1.R.C.value, init_1.R.P.value
    ('AT2', 'HIGH')
    >>> item = {'name': 'Toggle TestState tran01',
    ...         'initial':[{'AnotherState':'AnotherState1(R)'}],
    ...         'final': [{'AnotherState': 'pop(R)'}],
    ...         'incoming': [{'Action': 'PP(R)'}],
    ...         'outgoing': [{"Pause":"PA()"}]}
    >>> ts = checkmate.tymata.transition.TransitionStorage(item, module_dict)
    >>> t = ts.factory()
    >>> init_1 = t.initial[0].factory(**t.initial[0].resolve())
    >>> init_1.partition_attribute
    ('R',)
    >>> init_1.R,
    (None,)
    
