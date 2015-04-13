We should be able to use python default types when defining exchanges:

    >>> import checkmate._module

    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> items = {
    ...     'partition_type': 'exchanges',
    ...     'signature': 'BO(F:bool)',
    ...     'codes_list': ['B1'],
    ...     'values_list': [True],
    ...     }
    >>> app.define_exchange(items)

    >>> import checkmate._storage
    >>> import checkmate.transition
    >>> import sample_app.application
    >>> item_out = {'name': 'Toggle TestState tran01',
    ...             'incoming': [{'ThirdAction': 'AL()'}],
    ...             'outgoing': [{'BO': 'B1(True)'}]}

    >>> module_dict = {'exchanges':[sample_app.exchanges]}

    >>> ts = checkmate._storage.TransitionStorage(item_out, module_dict)

    >>> delattr(sample_app.exchanges, 'BO')

