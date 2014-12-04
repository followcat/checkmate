we can match R with R2 when we do collcet runs
    a defined transition with incoming AP(R) matching outgoing AP(R2)
        >>> import sample_app.application
        >>> import checkmate._storage
        >>> import checkmate.transition
        >>> a = sample_app.application.TestData()
        >>> module_dict = {'states': [sample_app.component.component_1_states], 'exchanges':[sample_app.exchanges]}
        >>> item_in = {'name': 'Toggle TestState tran01', 'initial': [{'AnotherState': 'AnotherState1()'}], 'outgoing': [{'ThirdAction': 'DA()'}], 'incoming': [{'Action': 'AP(R)'}], 'final': [{'AnotherState': 'append(R)'}]}
        >>> item_out = {'name': 'Toggle TestState tran01', 'incoming': [{'AnotherReaction': 'ARE()'}], 'outgoing': [{'Action': 'AP(R2)'}]}
        >>> ts = checkmate._storage.TransitionStorage(item_in, module_dict)
        >>> t_in = checkmate.transition.Transition(tran_name=item_in['name'], initial=ts['initial'], incoming=ts['incoming'], final=ts['final'], outgoing=ts['outgoing'])
        >>> ts = checkmate._storage.TransitionStorage(item_out, module_dict)
        >>> t_out = checkmate.transition.Transition(tran_name=item_out['name'], initial=ts['initial'], incoming=ts['incoming'], final=ts['final'], outgoing=ts['outgoing'])
        >>> c1 = a.components['C1']
        >>> c2 = a.components['C2']
        >>> copy_t1 = c1.state_machine.transitions[1]
        >>> copy_t2 = c2.state_machine.transitions[2]
        >>> c1.state_machine.transitions[1] = t_in
        >>> c2.state_machine.transitions[2] = t_out
        >>> inc = c1.state_machine.transitions[1].incoming[0]
        >>> (inc.code, inc.resolved_arguments)
        ('AP', OrderedDict())
        >>> out = c2.state_machine.transitions[2].outgoing[0]
        >>> (out.code, out.resolved_arguments['R'].C.value, out.resolved_arguments['R'].P.value)
        ('AP', 'AT2', 'HIGH')
        >>> runs = a.run_collection
        >>> len(runs)
        4
        >>> 'AP' in [t.incoming[0].code for t in runs[0].walk() if len(t.incoming) > 0]
        True

    a defined transition with incoming AP(R2) matching outgoing AP(R)
        >>> a = sample_app.application.TestData()
        >>> module_dict = {'states': [sample_app.component.component_1_states], 'exchanges':[sample_app.exchanges]}
        >>> item_in = {'name': 'Toggle TestState tran01', 'initial': [{'AnotherState': 'AnotherState1()'}], 'outgoing': [{'ThirdAction': 'DA()'}], 'incoming': [{'Action': 'AP(R2)'}], 'final': [{'AnotherState': 'append(R2)'}]}
        >>> item_out = {'name': 'Toggle TestState tran01', 'incoming': [{'AnotherReaction': 'ARE()'}], 'outgoing': [{'Action': 'AP(R)'}]}
        >>> ts = checkmate._storage.TransitionStorage(item_in, module_dict)
        >>> t_in = checkmate.transition.Transition(tran_name=item_in['name'], initial=ts['initial'], incoming=ts['incoming'], final=ts['final'], outgoing=ts['outgoing'])
        >>> ts = checkmate._storage.TransitionStorage(item_out, module_dict)
        >>> t_out = checkmate.transition.Transition(tran_name=item_out['name'], initial=ts['initial'], incoming=ts['incoming'], final=ts['final'], outgoing=ts['outgoing'])
        >>> c1 = a.components['C1']
        >>> c2 = a.components['C2']
        >>> c1.state_machine.transitions[1] = t_in
        >>> c2.state_machine.transitions[2] = t_out
        >>> inc = c1.state_machine.transitions[1].incoming[0]
        >>> (inc.code, inc.resolved_arguments['R'].C.value, inc.resolved_arguments['R'].P.value)
        ('AP', 'AT2', 'HIGH')
        >>> out = c2.state_machine.transitions[2].outgoing[0]
        >>> (out.code, out.resolved_arguments)
        ('AP', OrderedDict())
        >>> runs = a.run_collection
        >>> len(runs)
        4
        >>> 'AP' in [t.incoming[0].code for t in runs[0].walk() if len(t.incoming) > 0]
        True
        >>> c1.state_machine.transitions[1] = copy_t1
        >>> c2.state_machine.transitions[2] = copy_t2

