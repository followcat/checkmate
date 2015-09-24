if the transition incoming comes like "AP(R1)", calling factory()
function without giving resolved_arguments will be ok.
    >>> import sample_app.application
    >>> a = sample_app.application.TestData()
    >>> t = a.components['C1'].engine.blocks[0]
    >>> t.incoming[0].factory().broadcast
    False
    >>> import checkmate.tymata.transition
    >>> item = {'name': 'Toggle TestState tran01', 
    ...         'initial': [{'AnotherState': '__init__()'}], 
    ...         'outgoing': [{'ThirdAction': 'DA()'}], 
    ...         'incoming': [{'Action': 'AP(R1)'}], 
    ...         'final': [{'AnotherState': 'append(R1)'}]}
    >>> t = checkmate.tymata.transition.make_transition(
    ...         item, [sample_app.exchanges],
    ...         [sample_app.component.component_1_states])
    >>> ex = t.incoming[0].factory()
    >>> ex.broadcast
    False
