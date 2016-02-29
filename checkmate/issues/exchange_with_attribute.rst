        >>> import sample_app.application
        >>> a = sample_app.application.TestData()
        >>> c = a.components['C1']
        >>> c.start()
        >>> i = c.engine.blocks[1].incoming[0].factory(R=1)
        >>> o = c.engine.blocks[1].process(c.states, [i])
        >>> c.states[1].value
        [{'R': 1}]

