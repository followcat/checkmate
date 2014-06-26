import checkmate._tree
import checkmate.sandbox
import checkmate.runtime.procedure
import sample_app.application


class TestProcedureRun1Threaded(checkmate.runtime.procedure.Procedure):
    """"""
    def __init__(self, application_class=sample_app.application.TestData, test=None):
        """
            >>> import checkmate.runtime._pyzmq
            >>> import checkmate.runtime._runtime
            >>> import sample_app.application
            >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, True)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> import sample_app.runtime.test_procedure
            >>> proc = sample_app.runtime.test_procedure.TestProcedureRun1Threaded()
            >>> proc.transitions.nodes[0].nodes[0].nodes[1].root.incoming[0].code
            'ARE'
            >>> proc.transitions.nodes[0].nodes[0].nodes[1].nodes[0].root.incoming[0].code
            'AP'
            >>> proc.transitions.nodes[0].nodes[0].nodes[1].nodes[0].nodes[0].root.incoming[0].code
            'DA'
            >>> proc(result=None, runtime=r)
            >>> r.stop_test()
        """
        super(TestProcedureRun1Threaded, self).__init__(application_class, test)
        box = checkmate.sandbox.Sandbox(application_class())
        c2 = box.application.components['C2']
        box(c2.state_machine.transitions[0])
        box.fill_procedure(self)

class TestProcedureRun2Threaded(checkmate.runtime.procedure.Procedure):
    """"""
    def __init__(self, application_class=sample_app.application.TestData, test=None):
        """
            >>> import checkmate.runtime._runtime
            >>> import checkmate.runtime.communication
            >>> import sample_app.application
            >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime.communication.Communication)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> proc = TestProcedureRun2Threaded()
            >>> proc.transitions.root.outgoing[0].code
            'PBRL'
            >>> proc.transitions.nodes[0].root.incoming[0].code
            'PBRL'
            >>> proc.transitions.nodes[0].nodes[0].nodes[0].root.incoming[0].code
            'DR'
            >>> r.stop_test()
        """
        super(TestProcedureRun2Threaded, self).__init__(application_class, test)
        box = checkmate.sandbox.Sandbox(application_class())
        c2 = box.application.components['C2']
        box(c2.state_machine.transitions[0])
        new_box = checkmate.sandbox.Sandbox(box.application)
        new_box(c2.state_machine.transitions[2])
        new_box.fill_procedure(self)

def build_procedure(sandbox):
    class TestProc(checkmate.runtime.procedure.Procedure):
        """"""
            
    proc = TestProc(type(sandbox.application))
    sandbox.fill_procedure(proc)
    return proc

def TestProcedureGenerator(application_class=sample_app.application.TestData):
    """
            >>> import sample_app.application
            >>> import sample_app.runtime.test_procedure
            >>> import checkmate.runtime._pyzmq
            >>> import checkmate.runtime._runtime
            >>> r = checkmate.runtime._runtime.Runtime(sample_app.application.TestData, checkmate.runtime._pyzmq.Communication, threaded=True)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> for g in sample_app.runtime.test_procedure.TestProcedureGenerator(sample_app.application.TestData):
            ...     g[0](r)
            >>> r.stop_test()
    """
    box = checkmate.sandbox.Sandbox(application_class())
    c2 = box.application.components['C2']
    #Skip the last two transitions as no outgoing sent to 'C1'
    #Skip the third transition from the last as 'C3' state does not match
    for _t in c2.state_machine.transitions[:1]:
        box(_t)
        yield build_procedure(box), box.transitions.root.owner, box.transitions.root.outgoing[0].code

