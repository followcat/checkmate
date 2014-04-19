import os
import os.path

import checkmate._tree
import checkmate.sandbox
import checkmate.test_data
import checkmate.parser.yaml_visitor
import checkmate.runtime.procedure
import checkmate.parser.feature_visitor


def build_procedure(sandbox, application_class):
    proc = checkmate.runtime.procedure.Procedure(application_class)
    sandbox.fill_procedure(proc)
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
        [<checkmate.transition.Transition object at ...
        >>> checkmate.runtime.test_plan.get_transitions_from_test(a, "feature") #doctest: +ELLIPSIS 
        [<checkmate.transition.Transition object at ...
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
        with open(os.sep.join([path, "itp.yaml"]), 'r') as _file:
            matrix = _file.read()
        _output = checkmate.parser.yaml_visitor.call_visitor(matrix)
        for data in _output['transitions']:
            array_list.append(data)
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
        >>> c1 = r.runtime_components['C1']
        >>> c2 = r.runtime_components['C2']
        >>> c3 = r.runtime_components['C3']
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
        >>> proc(r)
        >>> r.stop_test()

    """
    _application = application_class()
    components = list(_application.components.keys())
    state_modules = []
    for name in components:
        state_modules.append(_application.components[name].state_module)
    transition_list = get_transitions_from_test(_application, "itp")

    for _transition in transition_list:
        box = checkmate.sandbox.Sandbox(_application, [_transition])
        box([_transition], foreign_transitions=True)
        yield build_procedure(box, application_class), box.exchanges.root.origin, box.exchanges.root.action, box.exchanges.root.destination


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
        >>> c1 = r.runtime_components['C1']
        >>> c2 = r.runtime_components['C2']
        >>> c3 = r.runtime_components['C3']
        >>> procedures = []
        >>> for p in checkmate.runtime.test_plan.TestProcedureFeaturesGenerator(sample_app.application.TestData):
        ...     procedures.append(p[0])
        >>> proc = procedures[0]
        >>> proc(r)
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
        yield build_procedure(box, application_class), box.exchanges.root.origin, box.exchanges.root.action, box.exchanges.root.destination

