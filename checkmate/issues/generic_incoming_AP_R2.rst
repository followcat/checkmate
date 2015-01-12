can't generic incoming "AP(R2)" as alway consider states'attribute_list first is resolve
    >>> import collections
    >>> import sample_app.application
    >>> import checkmate.sandbox
    >>> import checkmate._storage
    >>> a = sample_app.application.TestData()
    >>> a.start()
    >>> module_dict = {'states': [sample_app.component.component_1_states], 'exchanges':[sample_app.exchanges]}
    >>> item = {'name': 'Toggle TestState tran01', 'initial':[{'AnotherState':'AnotherState1()'}], 'final': [{'AnotherState': 'AnotherState1(R2)'}], 'incoming': [{'Action': 'AP(R2)'}]}
    >>> ts = checkmate._storage.TransitionStorage(item, module_dict)
    >>> t = ts.factory()
    >>> t.incoming[0].code, t.incoming[0].resolved_arguments['R'].C.value, t.incoming[0].resolved_arguments['R'].P.value
    ('AP', 'AT2', 'HIGH')
    >>> a.components['C1'].states[1].attribute_list()
    {'R': None}
    >>> t.is_matching_initial(a.components['C1'].states)
    True
    >>> exchanges = t.generic_incoming(a.components['C1'].states)
    >>> ex = exchanges[0]
    >>> ex.R.C.value, ex.R.P.value
    ('AT2', 'HIGH')
    >>> t.is_matching_incoming(exchanges)
    True

When filling the generic incmoing for a component with default_state_value=False,
the attributes' values are set to None but the exchange value is filled:
    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> c1 = app.components['C1']
    >>> app.start(default_state_value=False)
    >>> c1.default_state_value
    False
    >>> tr = c1.state_machine.transitions[1]
    >>> ex = tr.generic_incoming(c1.states)
    >>> ex[0].R.C.value
    >>> ex[0].value
    'AP'

