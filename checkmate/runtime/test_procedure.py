import checkmate._tree
import checkmate.test_data
import checkmate.runtime.procedure

class TestProcedure(checkmate.runtime.procedure.Procedure):
    """"""
    def __init__(self, test=None):
        """
            >>> import checkmate.test_data
            >>> import checkmate.runtime._runtime
            >>> import checkmate.runtime.communication
            >>> a = checkmate.test_data.App()
            >>> r = checkmate.runtime._runtime.Runtime(a, checkmate.runtime.communication.Communication())
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> proc = TestProcedure()
            >>> proc.exchanges.root
            []
            >>> proc.exchanges.nodes[0].root.action
            'AC'
            >>> proc.exchanges.nodes[0].root.origin
            'C2'
            >>> proc.exchanges.nodes[0].root.destination
            'C1'
            >>> proc.exchanges.nodes[0].nodes[0].root.action
            'RE'
            >>> proc.exchanges.nodes[0].nodes[0].root.origin
            'C1'
            >>> proc.exchanges.nodes[0].nodes[0].root.destination
            'C3'
            >>> proc(result=None, system_under_test=['C1'])
            Traceback (most recent call last):
            ...
            Exception: Not exchange RE received by component C3
        """
        super(TestProcedure, self).__init__(test)
        a = checkmate.test_data.App()
        c1 = a.components['C1']
        c2 = a.components['C2']
        c3 = a.components['C3']
        a.start()
        transition = c2.state_machine.transitions[0]
        self.exchanges = checkmate._tree.Tree(transition.generic_incoming(c2.states), [])
        for _e in transition.process(c2.states, self.exchanges.root):
            _e.origin_destination(c2.name, c1.name)
            self.exchanges.add_node(checkmate._tree.Tree(_e, []))
        transition = c1.state_machine.transitions[0]
        for _e in transition.process(c1.states, [self.exchanges.nodes[0].root]):
            _e.origin_destination(c1.name, c3.name)
            self.exchanges.nodes[0].add_node(checkmate._tree.Tree(_e, []))
        self.components = ('C1', 'C2', 'C3')


class TestProcedureThreaded(checkmate.runtime.procedure.Procedure):
    """"""
    def __init__(self, test=None):
        """
            >>> import checkmate.test_data
            >>> import checkmate.runtime._runtime
            >>> import checkmate.runtime._pyzmq
            >>> a = checkmate.test_data.App()
            >>> r = checkmate.runtime._runtime.Runtime(a, checkmate.runtime.communication.Communication())
            >>> r.setup_environment(['C1'])
            >>> r.start_test()
            >>> proc = TestProcedureThreaded()
            >>> proc.exchanges.root
            []
            >>> proc.exchanges.nodes[0].nodes[1].root.action
            'ARE'
            >>> proc.exchanges.nodes[0].nodes[1].nodes[0].root.action
            'AP'
            >>> proc.exchanges.nodes[0].nodes[1].nodes[0].nodes[0].root.action
            'RL'
            >>> proc.exchanges.nodes[0].nodes[1].nodes[0].nodes[0].nodes[0].root.action
            'PP'
            >>> proc.exchanges.nodes[0].nodes[1].nodes[0].nodes[0].nodes[0].nodes[1].root.action
            'PA'
        """
        super(TestProcedureThreaded, self).__init__(test)
        a = checkmate.test_data.App()
        c1 = a.components['C1']
        c2 = a.components['C2']
        c3 = a.components['C3']
        a.start()
        transition = c2.state_machine.transitions[0]
        self.exchanges = checkmate._tree.Tree(transition.generic_incoming(c2.states), [])
        for _e in transition.process(c2.states, [self.exchanges.root]):
            self.exchanges.add_node(checkmate._tree.Tree(_e, []))
        transition = c1.state_machine.transitions[0]
        for _e in transition.process(c1.states, [self.exchanges.nodes[0].root]):
            self.exchanges.nodes[0].add_node(checkmate._tree.Tree(_e, []))
        transition = c3.state_machine.transitions[0]
        for _e in transition.process(c3.states, [self.exchanges.nodes[0].nodes[0].root]):
            self.exchanges.nodes[0].nodes[0].add_node(checkmate._tree.Tree(_e, []))
        transition = c2.state_machine.transitions[1]
        for _e in transition.process(c2.states, [self.exchanges.nodes[0].nodes[1].root]):
            self.exchanges.nodes[0].nodes[1].add_node(checkmate._tree.Tree(_e, []))
        transition = c1.state_machine.transitions[1]
        for _e in transition.process(c1.states, [self.exchanges.nodes[0].nodes[1].nodes[0].root]):
            self.exchanges.nodes[0].nodes[1].nodes[0].add_node(checkmate._tree.Tree(_e, []))
        transition = c3.state_machine.transitions[1]
        for _e in transition.process(c3.states, [self.exchanges.nodes[0].nodes[1].nodes[0].nodes[0].root]):
            self.exchanges.nodes[0].nodes[1].nodes[0].nodes[0].add_node(checkmate._tree.Tree(_e, []))
        transition = c1.state_machine.transitions[2]
        for _e in c1.process([self.exchanges.nodes[0].nodes[1].nodes[0].nodes[0].nodes[0].root]):
            self.exchanges.nodes[0].nodes[1].nodes[0].nodes[0].nodes[0].add_node(checkmate._tree.Tree(_e, []))
        self.components = ('C1', 'C2', 'C3')

