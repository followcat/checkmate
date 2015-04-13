This shows how to define an exchange using a list as attribute.

    >>> import checkmate._module
    >>> import checkmate.partition_declarator
    >>> import sample_app.application
    >>> import sample_app.exchanges
    >>> import sample_app.component.component_1_states

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
    <checkmate._storage.PartitionStorage object at ...
    >>> module['exchanges'] = exchange_module
    >>> checkmate.partition_declarator.make_partition(module,
    ...     ex_items) #doctest: +ELLIPSIS
    <checkmate._storage.PartitionStorage object at ...

Creation of the transition.

    >>> item_in = {'name': 'Receive exchange list partition',
    ...     'initial': [],
    ...     'incoming': [{'Exchange': 'EX(IT, IT, IT)'}],
    ...     }

    >>> module = {
    ...     'states': [sample_app.component.component_1_states],
    ...     'exchanges':[sample_app.exchanges]}
    >>> ts = checkmate._storage.TransitionStorage(item_in, module)
    >>> t_in = ts.factory()
    >>> c1 = sample_app.application.TestData().components['C1']
    >>> c1.start()

Let's create an exchange from a list of codes:

    >>> ex = t_in.generic_incoming(c1.states)[0]

Based on the signature parameter type, the attribute will be created
differently. A POSITIONAL_OR_KEYWORD parameter is instantiated using
the annotated type:

    >>> sample_app.exchanges.Exchange._sig.parameters['I']._kind
    <_ParameterKind: 'POSITIONAL_OR_KEYWORD'>
    >>> type(ex.I)
    <class 'sample_app.data.Item'>
    >>> ex.I.value
    'item'

A VAR_POSITIONAL parameter is turned into a list:

    >>> sample_app.exchanges.Exchange._sig.parameters['L']._kind
    <_ParameterKind: 'VAR_POSITIONAL'>
    >>> type(ex.L)
    <class 'list'>
    >>> len(ex.L)
    2

The items in the list will be instantiated using the type
from annotation.

    >>> sample_app.exchanges.Exchange._sig.parameters['L']._annotation
    <class 'sample_app.data.Item'>
    >>> ex.L[0] #doctest: +ELLIPSIS
    <sample_app.data.Item object at ...
    >>> ex.L[0].value
    'item'

Rollback all changes in the common modules.

    >>> delattr(exchange_module, 'Exchange')
    >>> delattr(data_structure_module, 'Item')
    >>>
