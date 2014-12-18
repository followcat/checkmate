import checkmate._tree
import checkmate.sandbox
import checkmate.runs


class TestProcedureRun1Threaded(checkmate.runs.Run):
    """"""
    def __init__(self, application_class):
        """
            >>> import checkmate.runtime._pyzmq
            >>> import checkmate.runtime._runtime
            >>> import sample_app.application
            >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, True)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> import sample_app.runtime.test_procedure
            >>> run = sample_app.runtime.test_procedure.TestProcedureRun1Threaded(sample_app.application.TestData)
            >>> proc = r.build_procedure(run, r.application)
            >>> proc.transitions.nodes[0].nodes[0].nodes[2].root.incoming[0].code
            'ARE'
            >>> proc.transitions.nodes[0].nodes[0].nodes[2].nodes[0].root.incoming[0].code
            'AP'
            >>> proc.transitions.nodes[0].nodes[0].nodes[2].nodes[0].nodes[1].root.incoming[0].code
            'DA'
            >>> r.execute(proc)
            >>> r.stop_test()
        """
        box = checkmate.sandbox.Sandbox(application_class())
        c2 = box.application.components['C2']
        box(c2.state_machine.transitions[0])
        super(TestProcedureRun1Threaded, self).__init__(box.transitions.root, box.transitions.nodes)


class TestProcedureRun2Threaded(checkmate.runs.Run):
    """"""
    def __init__(self, application_class):
        """
            >>> import checkmate.runtime._runtime
            >>> import checkmate.runtime.communication
            >>> import sample_app.application
            >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime.communication.Communication)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> run = TestProcedureRun2Threaded(sample_app.application.TestData)
            >>> proc = r.build_procedure(run)
            >>> proc.transitions.root.outgoing[0].code
            'PBRL'
            >>> proc.transitions.nodes[0].root.incoming[0].code
            'PBRL'
            >>> proc.transitions.nodes[0].nodes[0].nodes[0].root.incoming[0].code
            'DR'
            >>> r.stop_test()
        """
        box = checkmate.sandbox.Sandbox(application_class())
        c2 = box.application.components['C2']
        box(c2.state_machine.transitions[0])
        new_box = checkmate.sandbox.Sandbox(box.application)
        transition_rl_index = [_t for _t in c2.state_machine.transitions
                               if _t.outgoing and _t.outgoing[0].code == 'RL']
        new_box(transition_rl_index[0])
        super(TestProcedureRun2Threaded, self).__init__(new_box.transitions.root, new_box.transitions.nodes)


def build_procedure(sandbox):
    class TestRun(checkmate.runs.Run):
        """"""
    run = TestRun(sandbox.transitions.root, sandbox.transitions.nodes)
    return run


def TestProcedureGenerator(application_class):
    """
            >>> import sample_app.application
            >>> import sample_app.runtime.test_procedure
            >>> import checkmate.runtime._pyzmq
            >>> import checkmate.runtime._runtime
            >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> for g in sample_app.runtime.test_procedure.TestProcedureGenerator(sample_app.application.TestData):
            ...     proc = r.build_procedure(g[0])
            ...     r.execute(proc)
            >>> r.stop_test()
    """
    box = checkmate.sandbox.Sandbox(application_class())
    c2 = box.application.components['C2']
    #Skip the last two transitions as no outgoing sent to 'C1'
    #Skip the third transition from the last as 'C3' state does not match
    for _t in c2.state_machine.transitions[:1]:
        box(_t)
        yield build_procedure(box), box.transitions.root.owner, box.transitions.root.outgoing[0].code
