In sample_app we should not generate a procedure from AnotherState1(R2)
itp transition when C1 'Append element ok tran01' transition's initial
state is AnotherState1(R1).

    >>> import sample_app.application
    >>> import checkmate.runs
    >>> import checkmate.runtime._runtime
    >>> ac = sample_app.application.TestData
    >>> cc = checkmate.runtime.communication.Communication
    >>> r = checkmate.runtime._runtime.Runtime(ac, cc)
    >>> exchange_module = r.application.exchange_module
    >>> state_modules = []
    >>> for name in list(r.application.components.keys()):
    ...     state_modules.append(
    ...         r.application.components[name].state_module)

Save transition which will be replaced

    >>> save_transition = \
    ...     r.application.components['C1'].engine.blocks[1]

Replace the second transition in component1 to initial is
AnotherState1(R1) 

    >>> new_items = {
    ...     'incoming': [{'Action': 'AP(R)'}], 
    ...     'name': 'Append element ok tran01', 
    ...     'initial': [{'AnotherState': 'AnotherState1(R1)'}], 
    ...     'final': [{'AnotherState': 'append(R)'}], 
    ...     'outgoing':[{'ThirdAction':'DA()'}]}
    >>> new_transition = \
    ...     checkmate.partition_declarator.make_transition(new_items,
    ...         [exchange_module], state_modules)
    >>> r.application.components['C1'].engine.blocks[1] = \
    ...     new_transition

Make an itp transition which initial state is AnotherState1(R2):

    >>> pre_items = {'incoming': [], 'name': '',
    ...              'initial': [], 'final': []}
    >>> run_items = {
    ...     'incoming': [{'Action': 'AP(R)'}],
    ...     'name': 'Append request C1 with AP',
    ...     'initial': [{'State': 'State2',
    ...                  'AnotherState': 'AnotherState1(R2)'}],
    ...     'final': [{'AnotherState': 'AnotherState1(R)'}]}
    >>> per_transition = \
    ...     checkmate.partition_declarator.make_transition(pre_items,
    ...         [exchange_module], state_modules)
    >>> run_transition = checkmate.partition_declarator.make_transition(
    ...                     run_items, [exchange_module], state_modules)

All state in sandbox.application will be set as the run_transition
initial state:

    >>> box = checkmate.sandbox.Sandbox(type(r.application),
    ...         r.application, [per_transition, run_transition])
    >>> state_list = box.application.state_list()
    >>> [_s.value for _s in state_list
    ...  if isinstance(_s,
    ...         sample_app.component.component_1_states.State)]
    [False]
    >>> [_s.R.C.value for _s in state_list
    ...  if isinstance(_s,
    ...         sample_app.component.component_1_states.AnotherState)]
    ['AT2']
    >>> [_s.value for _s in state_list
    ...  if isinstance(_s,
    ...         sample_app.component.component_3_states.Acknowledge)]
    [False]

Can not run sandbox:

    >>> box(checkmate.runs.Run(run_transition), itp_run=True)
    False

Recover transition:

    >>> r.application.components['C1'].engine.blocks[1] = \
    ...     save_transition
