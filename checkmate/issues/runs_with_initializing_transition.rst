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
        >>> application_class = sample_app.application.TestData
        >>> exchange_definition = {
        ...    'partition_type': 'exchanges',
        ...    'signature': 'ForthAction',
        ...    'codes_list': ['AF()'],
        ...    'values_list': ['AF'],
        ...    'full_description': None,
        ...    'attributes': {'class_destination':['Component_1']},
        ...    'define_attributes': {}
        ... }
        >>> exchange_definition2 = {
        ...    'partition_type': 'exchanges',
        ...    'signature': 'InitAction',
        ...    'codes_list': ['INTAC()'],
        ...    'values_list': ['INTAC'],
        ...    'full_description': None,
        ...    'attributes': {'class_destination':['Component_2']},
        ...    'define_attributes': {}
        ... }
        >>> if hasattr(application_class,
        ...     application_class._origin_exchanges_attribute):
        ...     delattr(application_class,
        ...         application_class._origin_exchanges_attribute)
        >>> app = sample_app.application.TestData()
        >>> app.define_exchange(exchange_definition)
        >>> app.define_exchange(exchange_definition2)
        >>> item_out = {'name': 'Initializing tran01',
        ...             'initializing': True,
        ...             'incoming': [{'InitAction': 'INIAC()'}],
        ...             'outgoing': [{'ForthAction': 'AF()'}]}
        >>> item_in = {'name': 'TestState tran02',
        ... 'incoming': [{'ForthAction': 'AF()'}],
        ... 'initial': [{'State': 'State1'}],
        ... 'final': [{'State': 'State2'}]}
        >>> t_out = checkmate.tymata.transition.make_transition(
        ...         item_out, [sample_app.exchanges],
        ...         [sample_app.component.component_1_states])
        >>> state1 = sample_app.component.component_1.Component_1
        >>> state2 = sample_app.component.component_2.Component_2
        >>> state2.instance_engines['C2'].blocks.append(t_out)
        >>> t_in = checkmate.tymata.transition.make_transition(
        ...         item_in, [sample_app.exchanges],
        ...         [sample_app.component.component_1_states])
        >>> state1.instance_engines['C1'].blocks.append(t_in)
        >>> state1.instance_engines['C1'].service_classes.append(
        ...     sample_app.exchanges.ForthAction)
        >>> state2.instance_engines['C2'].service_classes.append(
        ...     sample_app.exchanges.InitAction)
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
        >>> runs = [_r for _r in
        ...     application_class.origin_runs_gen(app)]
        >>> initializing_run = [r for r in app.run_collection()
        ...      if r.root.outgoing[0].code=='AF'][0]
        >>> initializing_run # doctest: +ELLIPSIS
        <checkmate.runs.Run object at ...
        >>> c1.context.states[0].value
        False
        >>> run1 = [r for r in app.run_collection()
        ...     if r.root.incoming[0].code=='PBPP'][0]
        >>> run1.root.incoming[0].code
        'PBPP'
        >>> r.execute(run1) # doctest: +ELLIPSIS
        >>> c1.context.states[0].value
        True
        >>> c3.context.states[0].value
        False
        >>> run1.compare_initial(app)
        False
        >>> run_list = checkmate.pathfinder._find_runs(app, run1, run1)

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
        >>> state1.instance_engines['C1'].service_classes.remove(
        ...     sample_app.exchanges.ForthAction)
        >>> state1.instance_engines['C1'].blocks.remove(t_in)
        >>> state2.instance_engines['C2'].blocks.remove(t_out)
        >>> delattr(application_class,
        ...     application_class._origin_exchanges_attribute)
        >>> delattr(application_class,
        ...     application_class._run_collection_attribute)
        >>> delattr(application_class,
        ...     application_class._starting_run_attribute)

