    >>> import checkmate.runs
    >>> import checkmate._module
    >>> import checkmate.tymata.transition
    >>> import checkmate.partition_declarator
    >>> import sample_app.application
    >>> import sample_app.component.component_1
    >>> import sample_app.component.component_2
    >>> exchange_module = sample_app.exchanges
    >>> data_structure_module = sample_app.data_structure
    >>> state_module = checkmate._module.get_module(
    ...                 'checkmate.application', 'states')
    >>> data_source = {
    ... 'exchanges': [{
    ...    'signature': 'ForthAction',
    ...    'codes_list': ['AF()'],
    ...    'values_list': ['AF'],
    ...    'full_description': None,
    ...    'attributes': {},
    ...    'define_attributes': {}}]
    ... }
    >>> de = checkmate.partition_declarator.Declarator(
    ...         data_structure_module, exchange_module,
    ...         state_module=state_module)
    >>> de.new_definitions(data_source)
    >>> item_in = {'name': 'TestState tran02',
    ...            'incoming': [{'ForthAction': 'AF()'}],
    ...            'outgoing': [{'Action': 'AC()'}]}
    >>> t = checkmate.tymata.transition.make_transition(
    ...         item_in, [sample_app.exchanges])
    >>> c2 = sample_app.component.component_2.Component_2
    >>> t_copy = c2.instance_engines['C2'].blocks[0]
    >>> c2.instance_engines['C2'].blocks[0] = t
    >>> app = sample_app.application.TestData()
    >>> app.start(default_state_value=False)
    >>> transitions = checkmate.runs.get_origin_transitions(app)
    >>> transitions[0].incoming[0].code
    'AF'
    >>> 'AC' in [t.outgoing[0].code for t in transitions]
    True
    >>> runs = app.run_collection()
    >>> 'AC' in [r.root.outgoing[0].code for r in runs]
    True

    Revert changes for further use in doctest:
    >>> c2.instance_engines['C2'].blocks[0] = t_copy
