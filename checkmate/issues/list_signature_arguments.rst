This shows how to parse a signature containing a list item.

    >>> import checkmate._module
    >>> import checkmate._exec_tools
    >>> import checkmate.partition_declarator
    >>> import sample_app.application
    >>> import sample_app.exchanges

    >>> exchange_module = checkmate._module.get_module(
    ...                     'sample_app.application', 'exchanges')
    >>> data_structure_module = checkmate._module.get_module(
    ...                             'sample_app.application', 'data')

Definition of the data structure for exchange attributes.

    >>> ds_items = {
    ...     'partition_type': 'data_structure',
    ...     'signature': 'Item',
    ...     'codes_list': ['IT'],
    ...     'values_list': ['item']
    ...     }

Definition of the exchange with list attribute.
The attribute is turn into a list by prefix '*':

    >>> ex_items = {                           
    ...     'partition_type': 'exchanges',
    ...     'signature': 'Exchange(I:Item, *L:Item)',
    ...     'codes_list': ['EX'],
    ...     'values_list': ['exlist']
    ...     }

Creation of the partitions.

    >>> module = {}
    >>> module['data_structure'] = data_structure_module
    >>> checkmate.partition_declarator.make_partition(module,
    ...     ds_items) #doctest: +ELLIPSIS
    (<InterfaceClass sample_app.data.IItem>, ...
    >>> module['exchanges'] = exchange_module
    >>> checkmate.partition_declarator.make_partition(module,
    ...     ex_items) #doctest: +ELLIPSIS
    (<InterfaceClass sample_app.exchanges.IExchange>, ...

The argument can be parsed and the list items are identified:

    >>> exchange_class = sample_app.exchanges.Exchange
    >>> res = checkmate._exec_tools.get_signature_arguments(
    ...     'EX(IT, LIT1, LIT2)', exchange_class)
    >>> sorted(res.items())
    [('I', 'IT'), ('L', ('LIT1', 'LIT2'))]


Rollback all changes in the common modules.

    >>> delattr(exchange_module, 'Exchange')
    >>> delattr(exchange_module, 'IExchange')
    >>> delattr(data_structure_module, 'Item')
    >>> delattr(data_structure_module, 'IItem')
    >>>
