import checkmate._tree
import checkmate.sandbox
import checkmate.test_data
import checkmate.service_registry
import checkmate.runtime.procedure
import checkmate.parser.feature_visitor


def build_procedure_with_initial(components, exchanges, output, initial, final, itp_transitions):
    import checkmate.runtime.procedure
    class TestProc(checkmate.runtime.procedure.Procedure):
        """"""
            
    proc = TestProc()
    setattr(proc, 'components', components)
    setattr(proc, 'exchanges', checkmate._tree.Tree(exchanges[0], [checkmate._tree.Tree(_o, []) for _o in output]))
    setattr(proc, 'initial', initial)
    setattr(proc, 'final', final)
    setattr(proc, 'itp_transitions', itp_transitions)
    return proc

def get_origin_component(exchange, components):
    for _c in components:
        if exchange.action in _c.outgoings:
            return _c

def TestProcedureInitialGenerator(application_class=checkmate.test_data.App, transition_list=None):
    """
        >>> import time
        >>> import checkmate.test_data
        >>> import sample_app.application
        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
        >>> r.setup_environment(['C1'])
        >>> r.start_test()
        >>> c1 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C1')
        >>> c2 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C2')
        >>> c3 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C3')
        >>> simulated_exchange = c2.context.state_machine.transitions[0].outgoing[0].factory()
        >>> o = c2.simulate(simulated_exchange) # doctest: +ELLIPSIS
        >>> time.sleep(1)
        >>> c1.context.states[0].value
        'False'
        >>> c3.context.states[0].value
        'True'
        >>> gen = checkmate.runtime.test_plan.TestProcedureInitialGenerator(sample_app.application.TestData)
        >>> procedures = []
        >>> for p in gen:
        ...     p[0].application = r.application
        ...     procedures.append(p[0])

        >>> proc = procedures[0]
        >>> proc.system_under_test = ['C1']
        >>> r.application.compare_states(proc.initial)
        False
        >>> proc.transform_to_initial()
        >>> time.sleep(2)
        >>> c1.context.states[0].value
        'True'
        >>> c3.context.states[0].value
        'False'
        >>> r.application.compare_states(proc.initial)
        True
        >>> proc.result = None
        >>> proc._run_from_startpoint(proc.exchanges)
        >>> r.application.compare_states(proc.final)
        True
        >>> r.stop_test()

    """
    a = application_class()
    a.start()
    if transition_list is None:
        a.get_initial_transitions()
        transition_list = a.initial_transitions
    components = list(a.components.keys())
    for _transition in transition_list:
        _incoming = _transition.incoming[0].factory()
        origin = get_origin_component(_incoming, list(a.components.values()))
        for _e in checkmate.service_registry.global_registry.server_exchanges(_incoming, origin.name):
            _o = a.components[_e.destination].process([_e])
            yield build_procedure_with_initial(components, [_e], _o, _transition.initial, _transition.final, transition_list), origin.name, _e.action, _e.destination


def build_procedure(sandbox):
    proc = checkmate.runtime.procedure.Procedure()
    sandbox.fill_procedure(proc)
    return proc

def TestProcedureFeaturesGenerator(application_class=checkmate.test_data.App):
    """
        >>> import checkmate.sandbox
        >>> import checkmate.parser.feature_visitor
        >>> import sample_app.application
        >>> _application = sample_app.application.TestData()
        >>> components = list(_application.components.keys())
        >>> state_modules = []
        >>> for name in components:
        ...         state_modules.append(_application.components[name].state_module)
        >>> transition_list = checkmate.parser.feature_visitor.get_transitions_from_features(_application.exchange_module, state_modules)
        >>> transition_list[0].incoming[0].code
        'PP'
        >>> box = checkmate.sandbox.Sandbox(_application, [transition_list[0]])
        >>> box.application.components['C1'].states[0].value == transition_list[0].initial[0].arguments[0][0]
        True
        >>> box.application.compare_states(transition_list[0].initial)
        True
        >>> box([transition_list[0]], foreign_transitions=True)
        True
        >>> len(box.initial)
        3

        >>> import checkmate.runtime._pyzmq
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime.test_plan
        >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
        >>> r.setup_environment(['C1'])
        >>> r.start_test()
        >>> c1 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C1')
        >>> c2 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C2')
        >>> c3 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C3')
        >>> procedures = []
        >>> for p in checkmate.runtime.test_plan.TestProcedureFeaturesGenerator(sample_app.application.TestData):
        ...     procedures.append(p[0])
        >>> proc = procedures[0]
        >>> proc(system_under_test=['C1'])
        >>> r.stop_test()
    """
    _application = application_class()
    components = list(_application.components.keys())
    state_modules = []
    for name in components:
        state_modules.append(_application.components[name].state_module)
    transition_list = checkmate.parser.feature_visitor.get_transitions_from_features(_application.exchange_module, state_modules)

    for _transition in transition_list:
        box = checkmate.sandbox.Sandbox(_application, [_transition])
        box([_transition], foreign_transitions=True)
        yield build_procedure(box), box.exchanges.root.origin, box.exchanges.root.action, box.exchanges.root.destination

