We should be able to define partitions from doctest
without any reference to yaml file.

    >>> import checkmate._module
    >>> import checkmate.application
    >>> import checkmate.data_structure
    >>> import checkmate.partition_declarator
    >>> state_module = checkmate._module.get_module(
    ...                     'checkmate.application', 'states')
    >>> exchange_module = checkmate._module.get_module(
    ...                     'checkmate.application', 'exchanges')
    >>> data_structure_module = checkmate._module.get_module(
    ...                             'checkmate.application', 'data')
    >>> de = checkmate.partition_declarator.Declarator(
    ...         data_structure_module, exchange_module,
    ...         state_module=state_module)
    >>> items = {
    ...     'partition_type': 'exchanges',
    ...     'signature': 'RC',
    ...     'codes_list': ['P1'],
    ...     'values_list': [True],
    ...     }
    >>> par = de.new_partition(items)

The partition should be returned by get_output()
even if no transition is provided.

    >>> de.get_output()['exchanges'] # doctest: +ELLIPSIS
    [<checkmate._storage.PartitionStorage object at ...

