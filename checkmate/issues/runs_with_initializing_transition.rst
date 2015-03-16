Run from initializing is special, it should be skip when running nose
plugin, it should not be used to transform to initial when executing
other runs
        >>> import time
        >>> import checkmate.sandbox
        >>> import checkmate.pathfinder
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import sample_app.application
        >>> import sample_app.component.component_1
        >>> import sample_app.component.component_2
        >>> exchange_module = sample_app.exchanges
        >>> data_structure_module = sample_app.data_structure
        >>> state_module = sample_app.component.component_1_states
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
        >>> item_out = {'name': 'Initializing tran01',
        ...             'initializing': True,
        ...             'outgoing': [{'ForthAction': 'AF()'}]}
        >>> item_in = {'name': 'TestState tran02',
        ... 'incoming': [{'ForthAction': 'AF()'}],
        ... 'initial': [{'State': 'State1'}],
        ... 'final': [{'State': 'State2'}]}
        >>> module_dict = {'exchanges':[sample_app.exchanges],
        ...     'states':[state_module]}
        >>> ts = checkmate._storage.TransitionStorage(item_out,
        ...         module_dict)
        >>> t_out = ts.factory()
        >>> state1 = sample_app.component.component_1.Component_1
        >>> state2 = sample_app.component.component_2.Component_2
        >>> state2.state_machine.transitions.append(t_out)
        >>> ts = checkmate._storage.TransitionStorage(item_in,
        ...         module_dict)
        >>> t_in = ts.factory()
        >>> state1.state_machine.transitions.append(t_in)
        >>> state1.service_classes.append(
        ...     sample_app.exchanges.ForthAction)
        >>> r = checkmate.runtime._runtime.Runtime(
        ...         sample_app.application.TestData,
        ...         checkmate.runtime._pyzmq.Communication,
        ...         threaded=True)
        >>> r.setup_environment(['C3'])
        >>> c1 = r.runtime_components['C1']
        >>> c2 = r.runtime_components['C2']
        >>> c3 = r.runtime_components['C3']
        >>> r.start_test()
        >>> time.sleep(1)
        >>> app = r.application
        >>> initializing_run = [r for r in app.run_collection
        ...      if r.root.outgoing[0].code=='AF'][0]
        >>> initializing_run # doctest: +ELLIPSIS
        <checkmate.runs.Run object at ...
        >>> c1.context.states[0].value
        False
        >>> run1 = app.run_collection[-1]
        >>> run1.root.outgoing[0].code
        'PBPP'
        >>> r.execute(run1) # doctest: +ELLIPSIS
        >>> c1.context.states[0].value
        True
        >>> c3.context.states[0].value
        False
        >>> run1.compare_initial(app)
        False
        >>> run_list = list(checkmate.pathfinder._find_runs(
        ...             app, run1).keys())

    Initializing transition runs should not be used to do transform to
    initial during executing runs
        >>> initializing_run in run_list
        False
   
    Skip test from initializing transition runs 
        >>> r.execute(initializing_run) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        unittest.case.SkipTest: Skip Initializing Test
        >>> r.stop_test()

    Revert changes for further use in doctest:
        >>> state1.service_classes.remove(
        ...     sample_app.exchanges.ForthAction)
        >>> state1.state_machine.transitions.remove(t_in)
        >>> state2.state_machine.transitions.remove(t_out)

