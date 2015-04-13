We can match R with R2 when we do collect runs
    A defined transition with incoming AP(R2) matching outgoing AP(R):
        >>> import checkmate._storage
        >>> import checkmate.transition
        >>> import sample_app.application
        >>> import sample_app.component.component_1
        >>> import sample_app.component.component_2
        >>> copy_t1 = sample_app.component.component_1.Component_1.state_machine.transitions[1]
        >>> copy_t2 = sample_app.component.component_2.Component_2.state_machine.transitions[2]

        >>> module_dict = {'states': [sample_app.component.component_1_states],
        ...                'exchanges':[sample_app.exchanges]}
        >>> item_in = {'name': 'Toggle TestState tran01',
        ...            'initial': [{'AnotherState': 'AnotherState1()'}],
        ...            'incoming': [{'Action': 'AP(R2)'}],
        ...            'final': [{'AnotherState': 'append(R2)'}],
        ...            'outgoing': [{'ThirdAction': 'DA()'}]}
        >>> item_out = {'name': 'Toggle TestState tran01',
        ...             'incoming': [{'AnotherReaction': 'ARE()'}],
        ...             'outgoing': [{'Action': 'AP(R)'}]}
        >>> ts = checkmate._storage.TransitionStorage(item_in, module_dict)
        >>> t_in = ts.factory()
        >>> ts = checkmate._storage.TransitionStorage(item_out, module_dict)
        >>> t_out = ts.factory()
        >>> sample_app.component.component_1.Component_1.state_machine.transitions[1] = t_in
        >>> sample_app.component.component_2.Component_2.state_machine.transitions[2] = t_out

        >>> a = sample_app.application.TestData()
        >>> c1 = a.components['C1']
        >>> c2 = a.components['C2']
        >>> inc = c1.state_machine.transitions[1].incoming[0]
        >>> (inc.code, inc.resolved_arguments['R'].C.value, inc.resolved_arguments['R'].P.value)
        ('AP', 'AT2', 'HIGH')
        >>> out = c2.state_machine.transitions[2].outgoing[0]
        >>> (out.code, out.resolved_arguments)
        ('AP', {})
        >>> runs = a.run_collection()
        >>> len(runs)
        4

    Matching the two AP() was done:
        >>> 'AP' in [t.incoming[0].code for t in runs[0].walk() if len(t.incoming) > 0]
        True

    We should now try to execute that transition:
        >>> import checkmate.runtime._runtime
        >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, True)
        >>> r.setup_environment(['C3'])
        >>> r.start_test()
        >>> runs = r.application.run_collection()
        >>> r.execute(runs[0])
        >>> r.stop_test()

    Revert changes in Component class definition for further use in doctest:
        >>> sample_app.component.component_1.Component_1.state_machine.transitions[1] = copy_t1
        >>> sample_app.component.component_2.Component_2.state_machine.transitions[2] = copy_t2
        >>> application_class = sample_app.application.TestData
        >>> delattr(application_class,
        ...     application_class._run_collection_attribute)

