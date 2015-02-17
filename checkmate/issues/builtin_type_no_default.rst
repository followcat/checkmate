    >>> import checkmate._module
    >>> import checkmate.application
    >>> import checkmate.partition_declarator
    >>> data_structure_module = checkmate._module.get_module(
    ...                              'checkmate.application', 'data')
    >>> ds_items = {
    ...     'partition_type': 'data_structure',
    ...     'signature': 'Item(IA:bool)',
    ...     'codes_list': ['IT'],
    ...     'values_list': ['item']
    ...     }
    >>> module = {}
    >>> module['data_structure'] = data_structure_module
    >>> checkmate.partition_declarator.make_partition(module,
    ...     ds_items) #doctest: +ELLIPSIS
    (<InterfaceClass checkmate.data.IItem>, ...
    >>> it_1 = data_structure_module.Item()
    >>> it_1.IA
    False
    >>> ia = True
    >>> it_2 = data_structure_module.Item(IA=ia)
    >>> it_2.IA
    True
    >>> it_1 == it_2
    False
    >>> it_3 = data_structure_module.Item(default=False)
    >>> it_3.IA is None
    True

    >>> storage = \
    ...     data_structure_module.Item.partition_storage.storage[0]
    >>> storage.match([it_1]) #doctest: +ELLIPSIS
    <checkmate.data.Item object at ...
    >>> storage.match([it_2]) #doctest: +ELLIPSIS
    <checkmate.data.Item object at ...
