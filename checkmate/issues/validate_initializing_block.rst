when component start, its initializing block will be simulated.

        >>> import time
        >>> import checkmate.sandbox
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> import sample_app.application
        >>> import sample_app.component.component_1
        >>> import sample_app.component.component_2
        >>> data_source = {
        ...    'partition_type': 'exchanges',
        ...    'signature': 'ForthAction',
        ...    'codes_list': ['AF()'],
        ...    'values_list': ['AF'],
        ...    'attributes': {},
        ...    'define_attributes': {}
        ... }
        >>> app = sample_app.application.TestData()
        >>> app.define_exchange(data_source)

        >>> item_out = {'name': 'Initializing tran01',
        ...             'initializing': True,
        ...             'outgoing': [{'ForthAction': 'AF()'}]}
        >>> item_in = {'name': 'TestState tran02',
        ... 'incoming': [{'ForthAction': 'AF()'}]}
        >>> module_dict = {'exchanges':[sample_app.exchanges]}
        >>> ts = checkmate._storage.TransitionStorage(item_out,
        ...         module_dict)
        >>> t_out = ts.factory()
        >>> state1 = sample_app.component.component_1.Component_1
        >>> state2 = sample_app.component.component_2.Component_2
        >>> state2.instance_engines['C2'].blocks.append(t_out)
        >>> ts = checkmate._storage.TransitionStorage(item_in,
        ...         module_dict)
        >>> t_in = ts.factory()
        >>> state1.instance_engines['C1'].blocks.append(t_in)
        >>> state1.instance_engines['C1'].service_classes.append(
        ...     sample_app.exchanges.ForthAction)
        >>> app = sample_app.application.TestData()
        >>> app.start()
        >>> app.initializing_outgoing #doctest: +ELLIPSIS
        [[<sample_app.exchanges.ForthAction object at ...

        >>> c1 = app.components['C1']
        >>> c2 = app.components['C2']
        >>> outgoing = c2.simulate(t_out)
        >>> outgoing[0].value
        'AF'

        >>> app_cls = sample_app.application.TestData
        >>> box = checkmate.sandbox.Sandbox(app_cls)
        >>> c1 = box.application.components['C1']
        >>> c1.validate(t_in)
        True

        >>> r = checkmate.runtime._runtime.Runtime(
        ...         sample_app.application.TestData,
        ...         checkmate.runtime._pyzmq.Communication,
        ...         threaded=True)
        >>> r.setup_environment(['C3'])

    send before starting the destination component of initializing
    block outgoing
        >>> r.application.stubs.sort()
        >>> r.application.stubs.reverse()
        >>> c1 = r.runtime_components['C1']
        >>> c2 = r.runtime_components['C2']
        >>> c3 = r.runtime_components['C3']
        >>> r.start_test()
        >>> time.sleep(1)
        >>> c1.validate(c1.context.engine.blocks[-1])
        True
        >>> r.stop_test()

    Revert changes for further use in doctest:
        >>> state1.instance_engines['C1'].service_classes.remove(
        ...     sample_app.exchanges.ForthAction)
        >>> state1.instance_engines['C1'].blocks.remove(t_in)
        >>> state2.instance_engines['C2'].blocks.remove(t_out)

