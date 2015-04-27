We can match R with R2 when we do collect runs
    A defined transition with incoming AP(R) matching outgoing AP(R2):
        >>> import checkmate.tymata.transition
        >>> import sample_app.application
        >>> import sample_app.component.component_1
        >>> import sample_app.component.component_2

        >>> item_in = {'name': 'Toggle TestState tran01', 'initial': [{'AnotherState': 'AnotherState1()'}], 'incoming': [{'Action': 'AP(R)'}], 'final': [{'AnotherState': 'append(R)'}], 'outgoing': [{'ThirdAction': 'DA()'}]}
        >>> item_out = {'name': 'Toggle TestState tran01', 'incoming': [{'AnotherReaction': 'ARE()'}], 'outgoing': [{'Action': 'AP(R2)'}]}
        >>> t_in = checkmate.tymata.transition.make_transition(
        ...         item_in, [sample_app.exchanges],
        ...         [sample_app.component.component_1_states])
        >>> t_out = checkmate.tymata.transition.make_transition(
        ...         item_out, [sample_app.exchanges],
        ...         [sample_app.component.component_1_states])
        >>> component_1 = sample_app.component.component_1.Component_1
        >>> component_2 = sample_app.component.component_2.Component_2
        >>> copy_t1 = component_1.instance_engines['C1'].blocks[1]
        >>> copy_t2 = component_2.instance_engines['C2'].blocks[2]
        >>> component_1.instance_engines['C1'].blocks[1] = t_in
        >>> component_2.instance_engines['C2'].blocks[2] = t_out

        >>> a = sample_app.application.TestData()
        >>> c1 = a.components['C1']
        >>> c2 = a.components['C2']
        >>> inc = c1.engine.blocks[1].incoming[0]
        >>> (inc.code, inc.resolved_arguments)
        ('AP', {})
        >>> out = c2.engine.blocks[2].outgoing[0]
        >>> (out.code, out.resolved_arguments['R'].C.value, out.resolved_arguments['R'].P.value)
        ('AP', 'AT2', 'HIGH')
        >>> runs = a.run_collection()
        >>> len(runs)
        4
        >>> 'AP' in [t.incoming[0].code for t in runs[0].walk() if len(t.incoming) > 0]
        True

    Revert changes in Component class definition for further use in doctest:
        >>> component_1.instance_engines['C1'].blocks[1] = copy_t1
        >>> component_2.instance_engines['C2'].blocks[2] = copy_t2
        >>> application_class = sample_app.application.TestData
        >>> delattr(application_class,
        ...     application_class._run_collection_attribute)

