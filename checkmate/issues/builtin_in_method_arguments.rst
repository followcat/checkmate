Partition.method_arguments should get False if an Exchange has bool datastructure
and given "(False)" signature.

    >>> import checkmate._exec_tools
    >>> import sample_app.application

Add TestExchange type of exchange in checkmate.

    >>> items = {
    ...     'partition_type': 'exchanges',
    ...     'signature': 'TestExchange(IA: bool)',
    ...     'codes_list': ['TE()'],
    ...     'values_list': ['TE']
    ...     }
    >>> app = sample_app.application.TestData()
    >>> app.define_exchange(items)
    >>> arguments = checkmate._exec_tools.get_signature_arguments(
    ...             "Test(False)", sample_app.exchanges.TestExchange)
    >>> sample_app.exchanges.TestExchange.method_arguments(arguments)
    {'IA': False}

Remove TestExchange in sample_app.
    >>> delattr(sample_app.exchanges, 'TestExchange')
