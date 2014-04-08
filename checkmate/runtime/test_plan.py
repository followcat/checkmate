import os
import os.path

import checkmate._tree
import checkmate.test_data
import checkmate.service_registry
import checkmate.parser.dtvisitor
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

def get_transitions_from_test(application, file_type):
    """
        >>> import checkmate.test_data
        >>> import checkmate.runtime.test_plan
        >>> a = checkmate.test_data.App()
        >>> checkmate.runtime.test_plan.get_transitions_from_test(a, "itp") #doctest: +ELLIPSIS 
        [<checkmate._storage.TransitionStorage object at ...
        >>> checkmate.runtime.test_plan.get_transitions_from_test(a, "feature") #doctest: +ELLIPSIS 
        [<checkmate._storage.TransitionStorage object at ...
    """

    if file_type not in ["itp", "feature"]:
        return []
    exchange_module = application.exchange_module
    state_modules = []
    for name in list(application.components.keys()):
            state_modules.append(application.components[name].state_module)
    path = os.path.dirname(exchange_module.__file__)
    array_list = []
    if file_type == "itp":
        with open(os.sep.join([path, "itp.rst"]), 'r') as _file:
            matrix = _file.read()
        _output = checkmate.parser.dtvisitor.call_visitor(matrix)
        for data in _output['transitions']:
            array_list.append(data['array_items'])
    if file_type == "feature":
        array_list = checkmate.parser.feature_visitor.get_array_list([os.path.join(os.getenv('CHECKMATE_HOME'), os.path.dirname(exchange_module.__file__), 'itp')])
    transitions = []
    for array_items in array_list:
        transitions.append(checkmate.partition_declarator.get_procedure_transition(array_items, exchange_module, state_modules))
    return transitions

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
        transition_list = get_transitions_from_test(a, "itp")
    components = list(a.components.keys())
    for _transition in transition_list:
        _incoming = _transition.incoming[0].factory()
        origin = get_origin_component(_incoming, list(a.components.values()))
        for _e in checkmate.service_registry.global_registry.server_exchanges(_incoming, origin.name):
            _o = a.components[_e.destination].process([_e])
            yield build_procedure_with_initial(components, [_e], _o, _transition.initial, _transition.final, transition_list), origin.name, _e.action, _e.destination

def TestProcedureFeaturesGenerator(application_class=checkmate.test_data.App, transition_list=None):
    a = application_class()
    a.start()
    components = list(a.components.keys())
    if transition_list is None:
        transition_list = get_transitions_from_test(a, "feature")
    for _transition in transition_list:
        _incoming = _transition.incoming[0].factory()
        origin = get_origin_component(_incoming, list(a.components.values()))
        for _e in checkmate.service_registry.global_registry.server_exchanges(_incoming, origin.name):
            _o = a.components[_e.destination].process([_e])
            yield build_procedure_with_initial(components, [_e], _o, _transition.initial, _transition.final, transition_list), origin.name, _e.action, _e.destination

