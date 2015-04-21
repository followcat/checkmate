When using a block defining AP(R) to process AP(R2),
the component should be able to execute the block:

    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> c1 = app.components['C1']
    >>> action_request = sample_app.data_structure.ActionRequest
    >>> r2 = action_request.storage_by_code('R2').factory()
    >>> ap_r2 = sample_app.exchanges.Action('AP', R=r2)
    >>> ap_r2.R.C.value, ap_r2.R.P.value
    ('AT2', 'HIGH')
    >>> b = c1.get_blocks_by_input([ap_r2])[0]
    >>> b.is_matching_initial(c1.states)
    True
    >>> sample_app.exchanges.ActionCode(True) in c1.process([ap_r2])
    True


define a block to to process AP(R2)
    >>> import sample_app.application
    >>> import checkmate._storage
    >>> a = sample_app.application.TestData()
    >>> a.start()
    >>> r1 = action_request.storage_by_code('R1').factory()
    >>> r2 = action_request.storage_by_code('R2').factory()
    >>> ap_r1 = sample_app.exchanges.Action('AP', R=r1)
    >>> ap_r2 = sample_app.exchanges.Action('AP', R=r2)
    >>> ap_r1.R.C.value, ap_r1.R.P.value
    ('AT1', 'NORM')
    >>> ap_r2.R.C.value, ap_r2.R.P.value
    ('AT2', 'HIGH')
    >>> c1_states = sample_app.component.component_1_states
    >>> c1 = a.components['C1']
    >>> module_dict = {'states': [c1_states],
    ...                'exchanges':[sample_app.exchanges]}
    >>> item = {'name': 'Toggle TestState tran01',
    ...         'initial': [{'AnotherState': 'AnotherState1()'}],
    ...         'outgoing': [{'ThirdAction': 'DA()'}],
    ...         'incoming': [{'Action': 'AP(R2)'}],
    ...         'final': [{'AnotherState': 'append(R2)'}]}
    >>> ts = checkmate._storage.TransitionStorage(item, module_dict)
    >>> t = ts.factory()
    >>> t.is_matching_incoming([ap_r1], c1.states)
    False
    >>> t.is_matching_incoming([ap_r2], c1.states)
    True
    >>> states = a.components['C1'].states
    >>> states[1].value
    >>> t.process(states, [ap_r2]) # doctest: +ELLIPSIS
    [<sample_app.exchanges.ThirdAction object at ...
    >>> states[1].value # doctest: +ELLIPSIS
    [{'R': <sample_app.data_structure.ActionRequest object at ...
    >>> states[1].value[0]['R'].C.value, states[1].value[0]['R'].P.value
    ('AT2', 'HIGH')


When using a block defining AP(R2) to process AP(R, default=False),
the component should be able to execute the block:

Setup:
    >>> import sample_app.application
    >>> import checkmate._storage
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> c1 = app.components['C1']
    >>> c1_states = sample_app.component.component_1_states
    >>> module_dict = {'states': [c1_states],
    ...                'exchanges':[sample_app.exchanges]}
    >>> item = {'name': 'Toggle TestState tran01',
    ...         'initial': [{'AnotherState': 'AnotherState1()'}],
    ...         'outgoing': [{'ThirdAction': 'DA()'}],
    ...         'incoming': [{'Action': 'AP(R2)'}],
    ...         'final': [{'AnotherState': 'append(R2)'}]}
    >>> ts = checkmate._storage.TransitionStorage(item, module_dict)
    >>> t = ts.factory()
    >>> saved_block = c1.engine.blocks[1]
    >>> c1.engine.blocks[1] = t

Default behavior. The exchange AP(R2) can't be processed.
    >>> ap = sample_app.exchanges.Action('AP')
    >>> ap.R.C.value, ap.R.P.value
    ('AT1', 'NORM')
    >>> t.is_matching_incoming([ap], c1.states)
    False
    >>> res = []
    >>> res = c1.process([ap]) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    checkmate.exception.NoBlockFound:
    >>> sample_app.exchanges.ActionCode(True) in res
    False

All state value to None. The exchange AP(R2) can be processed and
the expected final state is reached.
    >>> ap = sample_app.exchanges.Action('AP', default=False)
    >>> ap.R.C.value, ap.R.P.value
    (None, None)
    >>> t.is_matching_incoming([ap], c1.states)
    True
    >>> sample_app.exchanges.ActionCode(True) in c1.process([ap])
    True
    >>> c1.states[1].R.C.value, c1.states[1].R.P.value
    ('AT2', 'HIGH')

Restore original block for further testing.
    >>> c1.engine.blocks[1] = saved_block
    >>>

