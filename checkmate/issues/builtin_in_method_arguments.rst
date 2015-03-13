Partition.method_arguments should get False if an Exchange has bool datastructure
and given "(False)" signature.

    >>> import checkmate._module
    >>> import checkmate._exec_tools
    >>> import checkmate.application
    >>> import checkmate.partition_declarator
    >>> state_module = checkmate._module.get_module(
    ...                    'checkmate.application', 'states')
    >>> exchange_module = checkmate._module.get_module(
    ...                       'checkmate.application', 'exchanges')
    >>> data_structure_module = checkmate._module.get_module(
    ...                             'checkmate.application', 'data')
    >>> de = checkmate.partition_declarator.Declarator(
    ...         data_structure_module,
    ...         exchange_module,
    ...         state_module=state_module)

Add TestExchange type of exchange in checkmate.

    >>> items = {
    ...     'partition_type': 'exchanges',
    ...     'signature': 'TestExchange(IA: bool)',
    ...     'codes_list': ['TE()'],
    ...     'values_list': ['TE']
    ...     }
    >>> de.new_partition(items)
    >>> arguments = checkmate._exec_tools.get_signature_arguments(
    ...             "Test(False)", checkmate.exchanges.TestExchange)
    >>> checkmate.exchanges.TestExchange.method_arguments(arguments)
    {'IA': False}

Remove TestExchange and it's InterfaceClass in checkmate.
    >>> delattr(checkmate.exchanges, 'TestExchange')
