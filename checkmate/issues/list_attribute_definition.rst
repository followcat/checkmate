This shows how to define an exchange using a list as attribute.

    >>> import checkmate._module
    >>> import checkmate.application
    >>> import checkmate.data_structure
    >>> import checkmate.partition_declarator

    >>> exchange_module = checkmate._module.get_module(
    ...                     'checkmate.application', 'exchanges')
    >>> data_structure_module = checkmate._module.get_module(
    ...                             'checkmate.application', 'data')

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
    (<InterfaceClass checkmate.data.IItem>, ...
    >>> module['exchanges'] = exchange_module
    >>> checkmate.partition_declarator.make_partition(module,
    ...     ex_items) #doctest: +ELLIPSIS
    (<InterfaceClass checkmate.exchanges.IExchange>, ...

Let's create an exchange from a list of codes:

    >>> _list = ['IT', 'IT']
    >>> ex = checkmate.exchanges.Exchange('I', _list)

Based on the signature parameter type, the attribute will be created
differently. A POSITIONAL_OR_KEYWORD parameter is instantiated using
the annotated type:

    >>> checkmate.exchanges.Exchange._sig.parameters['I']._kind
    <_ParameterKind: 'POSITIONAL_OR_KEYWORD'>
    >>> type(ex.I)
    <class 'checkmate.data.Item'>
    >>> ex.I.value == 'item'
    True

A VAR_POSITIONAL parameter is turned into a list:

    >>> checkmate.exchanges.Exchange._sig.parameters['L']._kind
    <_ParameterKind: 'VAR_POSITIONAL'>
    >>> type(ex.L)
    list
    >>> len(ex.L) == len(_list)
    True

The items in the list will be instantiated using the type
from annotation.

    >>> checkmate.exchanges.Exchange._sig.parameters['L']._annotation
    <class 'checkmate.data.Item'>
    >>> ex.L[0] #doctest: +ELLIPSIS
    <checkmate.data.Item object at ...
    >>> ex.L[0].value == 'item'
    True

Rollback all changes in the common modules.

    >>> delattr(exchange_module, 'Exchange')
    >>> delattr(exchange_module, 'IExchange')
    >>> delattr(data_structure_module, 'Item')
    >>> delattr(data_structure_module, 'IItem')
    >>>
