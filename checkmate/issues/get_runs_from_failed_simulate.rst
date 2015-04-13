Should not get Runs when simulate has no outgoing. 

        >>> import os
        >>> import checkmate._module
        >>> import checkmate._storage
        >>> import checkmate.component
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
        ...     'instance_transitions': {},
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
        >>> module_dict = {'exchanges':[sample_app.exchanges]}
        >>> ts = checkmate._storage.TransitionStorage(item_out,
        ...         module_dict)
        >>> t_out = ts.factory()
        >>> C1 = sample_app.component.component_1.Component_1
        >>> C1.state_machine.transitions.append(t_out)
        >>> ts = checkmate._storage.TransitionStorage(item_in,
        ...         module_dict)
        >>> t_in = ts.factory()
        >>> Dummy = sample_app.component.dummycomponent.DummyComponent 
        >>> Dummy.state_machine.transitions.append(t_in)
        >>> a = sample_app.application.TestData() 
        >>> len(a.run_collection())
        4

    Revert changes for further use in doctest:
        >>> C1.state_machine.transitions.remove(t_out)
        >>> del sample_app.component.dummycomponent
        >>> del sample_app.exchanges.ForthAction
        >>> application_class = sample_app.application.TestData
        >>> delattr(application_class,
        ...     application_class._run_collection_attribute)
        >>> os.remove(class_file)
