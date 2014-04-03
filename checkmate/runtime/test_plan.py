import checkmate.sandbox
import checkmate.test_data
import checkmate.runtime.procedure
import checkmate.parser.feature_visitor


def build_procedure(sandbox):
    proc = checkmate.runtime.procedure.Procedure()
    sandbox.fill_procedure(proc)
    return proc


def _initial_generator_doctest():
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
        >>> r.application.compare_states(proc.initial)
        False
        >>> proc(['C1'])
        >>> r.stop_test()

    """
    pass


def TestProcedureInitialGenerator(application_class=checkmate.test_data.App, transition_list=None):
    _application = application_class()
    components = list(_application.components.keys())
    state_modules = []
    for name in components:
        state_modules.append(_application.components[name].state_module)
    _application.get_initial_transitions()
    transition_list = _application.initial_transitions

    for _transition in transition_list:
        box = checkmate.sandbox.Sandbox(_application, [_transition])
        box([_transition], foreign_transitions=True)
        yield build_procedure(box), box.exchanges.root.origin, box.exchanges.root.action, box.exchanges.root.destination


def _feature_generator_doctest():
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
    pass


def TestProcedureFeaturesGenerator(application_class=checkmate.test_data.App):
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

