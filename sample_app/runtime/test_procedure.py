import checkmate._tree
import checkmate.sandbox
import checkmate.test_data
import checkmate.runtime.procedure


class TestProcedureRun1Threaded(checkmate.runtime.procedure.Procedure):
    """"""
    def __init__(self, application_class=checkmate.test_data.App, test=None):
        """
            >>> import checkmate.test_data
            >>> import checkmate.runtime._runtime
            >>> import checkmate.runtime.communication
            >>> r = checkmate.runtime._runtime.Runtime(checkmate.test_data.App, checkmate.runtime._pyzmq.Communication, True)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> import sample_app.runtime.test_procedure
            >>> proc = sample_app.runtime.test_procedure.TestProcedureRun1Threaded()
            >>> proc.exchanges.nodes[1].root.action
            'ARE'
            >>> proc.exchanges.nodes[1].nodes[0].root.action
            'AP'
            >>> proc.exchanges.nodes[1].nodes[0].nodes[0].root.action
            'DA'
            >>> proc(result=None, system_under_test=['C1'])
            >>> r.stop_test()
        """
        super(TestProcedureRun1Threaded, self).__init__(test)
        a = application_class()
        c1 = a.components['C1']
        c2 = a.components['C2']
        c3 = a.components['C3']
        a.start()
        transition = c2.state_machine.transitions[0]
        self.initial = [_s.storage[0] for (_i, _s) in c1.state_machine.states] + [_s.storage[0] for (_i, _s) in c3.state_machine.states]
        self.exchanges = checkmate._tree.Tree(c2.process(transition.generic_incoming(c2.states))[0], [])
        for _e in c1.process([self.exchanges.root]):
            self.exchanges.add_node(checkmate._tree.Tree(_e, []))
        for _e in c3.process([self.exchanges.nodes[0].root]):
            self.exchanges.nodes[0].add_node(checkmate._tree.Tree(_e, []))
        for _e in c2.process([self.exchanges.nodes[1].root]):
            self.exchanges.nodes[1].add_node(checkmate._tree.Tree(_e, []))
        for _e in c1.process([self.exchanges.nodes[1].nodes[0].root]):
            self.exchanges.nodes[1].nodes[0].add_node(checkmate._tree.Tree(_e, []))

class TestProcedureRun2Threaded(checkmate.runtime.procedure.Procedure):
    """"""
    def __init__(self, application_class=checkmate.test_data.App, test=None):
        """
            >>> import checkmate.test_data
            >>> import checkmate.runtime._runtime
            >>> import checkmate.runtime.communication
            >>> r = checkmate.runtime._runtime.Runtime(checkmate.test_data.App, checkmate.runtime.communication.Communication)
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> proc = TestProcedureRun2Threaded()
            >>> proc.exchanges.root.action
            'RL'
            >>> proc.exchanges.nodes[0].root.action
            'DR'
            >>> r.stop_test()
        """
        super(TestProcedureRun2Threaded, self).__init__(test)
        a = application_class()
        c1 = a.components['C1']
        c2 = a.components['C2']
        c3 = a.components['C3']
        a.start()
        transition = c2.state_machine.transitions[0]
        local_exchanges = checkmate._tree.Tree(c2.simulate(transition.outgoing[0].factory())[0], [])
        for _e in c1.process([local_exchanges.root]):
            local_exchanges.add_node(checkmate._tree.Tree(_e, []))
        for _e in c3.process([local_exchanges.nodes[0].root]):
            local_exchanges.nodes[0].add_node(checkmate._tree.Tree(_e, []))
        for _e in c2.process([local_exchanges.nodes[1].root]):
            local_exchanges.nodes[1].add_node(checkmate._tree.Tree(_e, []))
        c1.process([local_exchanges.nodes[1].nodes[0].root])

        transition = c2.state_machine.transitions[2]
        self.exchanges = checkmate._tree.Tree(c2.simulate(transition.outgoing[0].factory())[0], [])
        self.initial = c3.get_transition_by_input([self.exchanges.root]).initial
        for _e in c3.process([self.exchanges.root]):
            self.exchanges.add_node(checkmate._tree.Tree(_e, []))

def build_procedure(sandbox):
    class TestProc(checkmate.runtime.procedure.Procedure):
        """"""
            
    proc = TestProc()
    setattr(proc, 'initial', sandbox.initial)
    setattr(proc, 'exchanges', sandbox.exchanges)
    return proc

def TestProcedureGenerator(application_class=checkmate.test_data.App):
    box = checkmate.sandbox.Sandbox(application_class())
    c2 = box.application.components['C2']
    #Skip the last two transitions as no outgoing sent to 'C1'
    #Skip the third transition from the last as 'C3' state does not match
    for _t in range(len(c2.state_machine.transitions)-5):
        box([c2.state_machine.transitions[_t]])
        yield build_procedure(box), box.exchanges.root.destination, box.exchanges.root.action

