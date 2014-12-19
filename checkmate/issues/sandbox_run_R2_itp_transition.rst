In sample_app shuold not generate a procedure from AnotherState1(R2) itp transition when C1 'Append element ok tran01' transition's initial state is AnotherState1(R1).
    >>> import sample_app.application
    >>> import checkmate._tree
    >>> import checkmate.runtime._runtime
    >>> ac = sample_app.application.TestData
    >>> cc = checkmate.runtime.communication.Communication
    >>> r = checkmate.runtime._runtime.Runtime(ac, cc)
    >>> exchange_module = r.application.exchange_module
    >>> state_modules = []
    >>> for name in list(r.application.components.keys()):
    ...     state_modules.append(r.application.components[name].state_module)

Replace the second transition in component1 to initial is AnotherState1(R1) 
    >>> new_items = {'incoming': [{'Action': 'AP(R)'}], 'name': 'Append element ok tran01', 'initial': [{'AnotherState': 'AnotherState1(R1)'}], 'final': [{'AnotherState': 'append(R)'}], 'outgoing':[{'ThirdAction':'DA()'}]}
    >>> new_transition = checkmate.partition_declarator.make_transition(new_items, [exchange_module], state_modules)
    >>> r.application.components['C1'].state_machine.transitions[1] = new_transition

Make an itp transition which initial state is AnotherState1(R2):
    >>> run_items = {'incoming': [{'Action': 'AP(R)'}], 'name': 'Append request C1 with AP', 'initial': [{'AnotherState': 'AnotherState1(R2)'}], 'final': [{'AnotherState': 'AnotherState1(R)'}]}
    >>> run_transition = checkmate.partition_declarator.make_transition(run_items, [exchange_module], state_modules)

Can not run sandbox:
    >>> box = checkmate.sandbox.Sandbox(r.application, [run_transition])
    >>> box(run_transition, foreign_transitions=True)
    False
