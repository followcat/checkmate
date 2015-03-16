We should be able to use python default types when defining exchanges:

    >>> import checkmate._module
    >>> import checkmate.partition_declarator

    >>> import sample_app.application
    >>> application_name = 'sample_app.application'
    >>> state_module = \
    ...     checkmate._module.get_module(application_name, 'states')
    >>> exchange_module = \
    ...     checkmate._module.get_module(application_name, 'exchanges')
    >>> data_structure_module = \
    ...     checkmate._module.get_module(application_name, 'data')
    >>> de = checkmate.partition_declarator.Declarator(
    ...             data_structure_module, exchange_module,
    ...             state_module=state_module)
    >>> items = {
    ...     'partition_type': 'exchanges',
    ...     'signature': 'BO(F:bool)',
    ...     'codes_list': ['B1'],
    ...     'values_list': [True],
    ...     }
    >>> par = de.new_partition(items)

    >>> import checkmate._storage
    >>> import checkmate.transition
    >>> import sample_app.application
    >>> item_out = {'name': 'Toggle TestState tran01',
    ...             'incoming': [{'ThirdAction': 'AL()'}],
    ...             'outgoing': [{'BO': 'B1(True)'}]}

    >>> module_dict = {'exchanges':[sample_app.exchanges]}

    >>> ts = checkmate._storage.TransitionStorage(item_out, module_dict)

    >>> delattr(sample_app.exchanges, 'BO')

