When using a transition defining AP(R) to process AP(R2),
the component should be able to execute the transition:

    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> c1 = app.components['C1']
    >>> r2 = app.data_value['ActionRequest'][1]['R2']
    >>> ap_r2 = sample_app.exchanges.Action('AP', R=r2)
    >>> ap_r2.R.C.value, ap_r2.R.P.value
    ('AT2', 'HIGH')
    >>> t = c1.get_transition_by_input([ap_r2])
    >>> t.is_matching_initial(c1.states)
    True
    >>> sample_app.exchanges.ActionCode(True) in c1.process([ap_r2])
    True


define a transition to to process AP(R2)
    >>> import sample_app.application
    >>> import checkmate._storage
    >>> a = sample_app.application.TestData()
    >>> a.start()
    >>> r1 = a.data_value['ActionRequest'][1]['R1']
    >>> r2 = a.data_value['ActionRequest'][1]['R2']
    >>> ap_r1 = sample_app.exchanges.Action('AP', R=r1)
    >>> ap_r2 = sample_app.exchanges.Action('AP', R=r2)
    >>> ap_r1.R.C.value, ap_r1.R.P.value
    ('AT1', 'NORM')
    >>> ap_r2.R.C.value, ap_r2.R.P.value
    ('AT2', 'HIGH')
    >>> module_dict = {'states': [sample_app.component.component_1_states], 'exchanges':[sample_app.exchanges]}
    >>> item = {'name': 'Toggle TestState tran01', 'initial': [{'AnotherState': 'AnotherState1()'}], 'outgoing': [{'ThirdAction': 'DA()'}], 'incoming': [{'Action': 'AP(R2)'}], 'final': [{'AnotherState': 'append(R2)'}]}
    >>> ts = checkmate._storage.TransitionStorage(item, module_dict)
    >>> t = checkmate.transition.Transition(tran_name=item['name'], initial=ts['initial'], incoming=ts['incoming'], final=ts['final'], outgoing=ts['outgoing'])
    >>> t.is_matching_incoming([ap_r1])
    False
    >>> t.is_matching_incoming([ap_r2])
    True
    >>> states = a.components['C1'].states
    >>> states[1].value
    >>> t.process(states, [ap_r2]) # doctest: +ELLIPSIS
    [<sample_app.exchanges.ThirdAction object at ...
    >>> states[1].value # doctest: +ELLIPSIS
    [{'R': <sample_app.data_structure.ActionRequest object at ...
    >>> states[1].value[0]['R'].C.value, states[1].value[0]['R'].P.value
    ('AT2', 'HIGH')

