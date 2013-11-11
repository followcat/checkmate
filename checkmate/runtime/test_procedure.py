import os, re
import pickle
import checkmate._tree
import checkmate.test_data
import checkmate.service_registry
import checkmate.runtime.procedure


def read_log(_f):
    class TestProc(checkmate.runtime.procedure.Procedure):
        """"""
            
    _e = pickle.load(_f)
    proc = TestProc()
    setattr(proc, 'exchanges', checkmate._tree.Tree(_e, []))
    _n = proc.exchanges
    try:
        while True:
            _e = pickle.load(_f)
            _n.add_node(checkmate._tree.Tree(_e, []))
            _n = _n.nodes[0]
    except EOFError:
        pass
    return proc

def TestLogProcedureGenerator(application_class=checkmate.test_data.App):
    a = application_class()
    for dirpath, dirnames, filenames in os.walk(os.getenv('CHECKMATE_LOG', './')):
        for _filename in [_f for _f in filenames if re.match('exchange-.*\.log', _f) is not None]:
            try:
                _f = open(os.path.join(dirpath, _filename), 'rb')
                yield read_log(_f), _filename
                _f.close()
            except FileNotFoundError:
                continue
            except EOFError:
                continue

def build_procedure_with_initial(exchanges, output, initial, final):
    class TestProc(checkmate.runtime.procedure.Procedure):
        """"""
            
    proc = TestProc()
    setattr(proc, 'exchanges', checkmate._tree.Tree(exchanges[0], [checkmate._tree.Tree(_o, []) for _o in output]))
    setattr(proc, 'initial', initial)
    setattr(proc, 'final', final)
    return proc

def get_origin_component(exchange, components):
    for _c in components:
        if exchange.action in _c.outgoings:
            return _c

def TestProcedureInitialGenerator(application_class=checkmate.test_data.App):
    """
        >>> import checkmate.test_data
        >>> import checkmate.runtime._runtime
        >>> import checkmate.runtime._pyzmq
        >>> import sample_app.application
        >>> import checkmate.runtime.test_procedure
        >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
        >>> r.setup_environment(['C1'])
        >>> r.start_test()
        >>> c1 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C1')
        >>> c2 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C2')
        >>> c3 = checkmate.runtime.registry.global_registry.getUtility(checkmate.component.IComponent, 'C3')
        >>> simulated_exchange = c2.context.state_machine.transitions[0].outgoing[0].factory()
        >>> o = c2.simulate(simulated_exchange) # doctest: +ELLIPSIS
        >>> c1.context.states[0].value
        'False'
        >>> c3.context.states[0].value
        'True'
        >>> gen = checkmate.runtime.test_procedure.TestProcedureInitialGenerator(sample_app.application.TestData)
        >>> for p in gen:
        ...     proc = p[0]

        >>> proc.system_under_test = ['C1']
        >>> proc.compare_states(proc.initial)
        False
        >>> proc.transform_to_initial()
        >>> c1.context.states[0].value
        'True'
        >>> c3.context.states[0].value
        'False'
        >>> proc.compare_states(proc.initial)
        True
        >>> proc.result = None
        >>> proc._run_from_startpoint(proc.exchanges)
        >>> proc.compare_states(proc.final)
        True
        >>> r.stop_test()

    """
    a = application_class()
    a.start()
    a.get_initial_transitions()
    _incoming = a.initial_transitions[0].incoming[0].factory()
    origin = get_origin_component(_incoming, list(a.components.values()))
    for _e in checkmate.service_registry.global_registry.server_exchanges(_incoming, origin):
        _o = a.components[_e.destination].process([_e])
        yield build_procedure_with_initial([_e], _o, a.initial_transitions[0].initial, a.initial_transitions[0].final), origin.name, _e.action, _e.destination

