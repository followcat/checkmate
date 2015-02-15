This comparison is taking the length of the target into account.
If a matching state is twice in the target, the comparison should
still be ok.

    >>> import sample_app.application
    >>> app = sample_app.application.TestData()
    >>> app.start()
    >>> c1 = app.components['C1']
    >>> c1.states[0].value
    True
    >>> t = c1.state_machine.transitions[0]
    >>> t.initial[0].values
    (True,)
    >>> app.compare_states(t.initial)
    True
    >>> target = t.initial + t.initial
    >>> app.compare_states(target)
    True
