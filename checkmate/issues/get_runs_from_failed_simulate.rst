Should not get Runs when simulate has no outgoing. 

        >>> import os
        >>> import checkmate._module
        >>> import checkmate.component
        >>> import checkmate.tymata.transition
        >>> import sample_app.application
        >>> import sample_app.component.component_1

        >>> data_source = {
        ...    'partition_type' :'exchanges',
        ...    'signature': 'ForthAction',
        ...    'codes_list': ['AF()'],
        ...    'values_list': ['AF'],
        ...    'attributes': {},
        ...    'define_attributes': {}
        ... }
        >>> app = sample_app.application.TestData()
        >>> app.define_exchange(data_source)

        >>> class_name = 'DummyComponent'
        >>> class_file = 'sample_app/component/dummycomponent.yaml'
        >>> component_module = checkmate._module.get_module(
        ...                         'sample_app.application',
        ...                         class_name.lower(), 'component')
        >>> exchange_module = sample_app.exchanges
        >>> data_structure_module = sample_app.data_structure
        >>> state_module = checkmate._module.get_module(
        ...                     'sample_app.application', 'states')
        >>> communication_list = \
        ...     sample_app.application.TestData.communication_list
        >>> d = {
        ...     'exchange_module': exchange_module,
        ...     'data_structure_module': data_structure_module,
        ...     '__module__': component_module.__name__,
        ...     'component_definition': class_file,
        ...     'instances': [{'name': 'DUMMY'}],
        ...     'communication_list': communication_list.keys()}
        >>> _file = open(class_file, 'w')
        >>> _file.close()
        >>> _class = checkmate.component.ComponentMeta(
        ...             class_name, (checkmate.component.Component,), d)
        >>> setattr(component_module, class_name, _class)
        >>> item_out = {
        ...     'name': 'Toggle TestState tran01',
        ...     'outgoing': [{'ForthAction': 'AF()'}]}
        >>> item_in = {
        ...     'name': 'Toggle TestState tran02',
        ...     'incoming': [{'ForthAction': 'AF()'}]}
        >>> t_out = checkmate.tymata.transition.make_transition(
        ...         item_out, [sample_app.exchanges])
        >>> C1 = sample_app.component.component_1.Component_1
        >>> C1.instance_engines['C1'].blocks.append(t_out)
        >>> t_in = checkmate.tymata.transition.make_transition(
        ...         item_in, [sample_app.exchanges])
        >>> Dummy = sample_app.component.dummycomponent.DummyComponent 
        >>> Dummy.instance_engines['DUMMY'].blocks.append(t_in)
        >>> a = sample_app.application.TestData() 
        >>> len(a.run_collection())
        4

    Revert changes for further use in doctest:
        >>> C1.instance_engines['C1'].blocks.remove(t_out)
        >>> del sample_app.component.dummycomponent
        >>> del sample_app.exchanges.ForthAction
        >>> application_class = sample_app.application.TestData
        >>> delattr(application_class,
        ...     application_class._origin_exchanges_attribute)
        >>> delattr(application_class,
        ...     application_class._run_collection_attribute)
        >>> os.remove(class_file)
