new a transition with initial like "__init__(R2)" then, get initial factory() to return a state with R=R2, ('AT2','HIGH')
    >>> import sample_app.application
    >>> a = sample_app.application.TestData()
    >>> import checkmate._storage
    >>> module_dict = {'states': [sample_app.component.component_1_states], 'exchanges':[sample_app.exchanges]}
    >>> item = {'name': 'Toggle TestState tran01', 'initial':[{'AnotherState':'__init__(R)'}], 'final': [{'AnotherState': 'pop(R)'}], 'incoming': [{'Action': 'PP(R)'}], 'outgoing': [{"Pause":"PA()"}]}
    >>> ts = checkmate._storage.TransitionStorage(item, module_dict, a.data_value)
    >>> t = checkmate.transition.Transition(tran_name=item['name'], incoming=ts['incoming'], outgoing=ts['outgoing'], initial=ts['initial'], final=ts['final'])
    >>> init_1 = t.initial[0].factory()
    >>> init_1.partition_attribute
    ('R',)
    >>> init_1.R.C.value, init_1.R.P.value
    ('AT1', 'NORM')
    >>> item = {'name': 'Toggle TestState tran01', 'initial':[{'AnotherState':'__init__(R2)'}], 'final': [{'AnotherState': 'pop(R2)'}], 'incoming': [{'Action': 'PP(R2)'}], 'outgoing': [{"Pause":"PA()"}]}
    >>> ts = checkmate._storage.TransitionStorage(item, module_dict, a.data_value)
    >>> t = checkmate.transition.Transition(tran_name=item['name'], incoming=ts['incoming'], outgoing=ts['outgoing'], initial=ts['initial'], final=ts['final'])
    >>> init_1 = t.initial[0].factory()
    >>> init_1.partition_attribute
    ('R',)
    >>> init_1.R.C.value, init_1.R.P.value
    ('AT2', 'HIGH')
    >>> item = {'name': 'Toggle TestState tran01', 'initial':[{'AnotherState':'__init__()'}], 'final': [{'AnotherState': 'pop(R)'}], 'incoming': [{'Action': 'PP(R)'}], 'outgoing': [{"Pause":"PA()"}]}
    >>> ts = checkmate._storage.TransitionStorage(item, module_dict, a.data_value)
    >>> t = checkmate.transition.Transition(tran_name=item['name'], incoming=ts['incoming'], outgoing=ts['outgoing'], initial=ts['initial'], final=ts['final'])
    >>> init_1 = t.initial[0].factory()
    >>> init_1.partition_attribute
    ()
