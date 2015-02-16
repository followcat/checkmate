
        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start()
        >>> t = c.state_machine.transitions[1]
        >>> i = t.incoming[0].factory(kwargs={'R': 1})
        >>> t.final[0].resolve(c.states, [i]) # doctest: +ELLIPSIS
        {'R': <sample_app.data_structure.ActionRequest object at ...
        >>> i = t.incoming[0].factory()
        >>> (i.value, [i.R.C.value, i.R.P.value])
        ('AP', ['AT1', 'NORM'])
        >>> t.final[0].resolve(c.states, [i]) # doctest: +ELLIPSIS
        {'R': <sample_app.data_structure.ActionRequest object at ...
