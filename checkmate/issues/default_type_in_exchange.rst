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

    >>> import checkmate.tymata.transition
    >>> import sample_app.application
    >>> item_out = {'name': 'Toggle TestState tran01',
    ...             'incoming': [{'ThirdAction': 'AL()'}],
    ...             'outgoing': [{'BO': 'B1(True)'}]}

    >>> t = checkmate.tymata.transition.make_transition(
    ...         item_out, [sample_app.exchanges])

    >>> delattr(sample_app.exchanges, 'BO')

