import checkmate._tree
import checkmate.sandbox
import checkmate.transition


class TransitionTree(checkmate._tree.Tree):
    """"""
    def __init__(self, transition, nodes=None):
        """
            >>> import checkmate._storage
            >>> import checkmate.transition
            >>> import sample_app.application
            >>> import sample_app.data_structure
            >>> incoming_list = [checkmate._storage.InternalStorage(sample_app.data_structure.IActionRequest, 'AC()', None, value='AC()')]
            >>> outgoing_list = [checkmate._storage.InternalStorage(sample_app.data_structure.IActionRequest, 'RE()', None, value='RE()'), checkmate._storage.InternalStorage(sample_app.data_structure.IActionRequest, 'ARE()', None, value='ARE()')]
            >>> test_transition = checkmate.transition.Transition(incoming = incoming_list, outgoing = outgoing_list)
            >>> tree = checkmate.runs.TransitionTree(test_transition)
            >>> (tree.root.incoming[0].code, tree.root.outgoing[0].code, tree.root.outgoing[1].code)
            ('AC', 'RE', 'ARE')
            >>> tt = checkmate.runs.TransitionTree(sample_app.application.TestData().components['C1'].state_machine.transitions[0])
            >>> tt.root #doctest: +ELLIPSIS
            <checkmate.transition.Transition object at ...
        """
        assert type(transition) == checkmate.transition.Transition
        if nodes is None:
            nodes = []
        super(TransitionTree, self).__init__(transition, nodes)

    def merge(self, tree):
        """
            >>> import checkmate._storage
            >>> import checkmate.transition
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> t1 = a.components['C1'].state_machine.transitions[0]
            >>> t2 = a.components['C3'].state_machine.transitions[0]
            >>> tree1 = checkmate.runs.TransitionTree(t1)
            >>> tree2 = checkmate.runs.TransitionTree(t2)
            >>> tree1.merge(tree2)
            True
            >>> len(tree1.nodes)
            1
            >>> tree1.nodes[0] == tree2
            True
        """
        if self.match_parent(tree):
            self.add_node(tree)
            return True
        merge = False
        for node in self.nodes:
            if node.merge(tree):
                merge = True
        return merge

    def match_parent(self, tree):
        """
            >>> import checkmate._storage
            >>> import checkmate.transition
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> t1 = a.components['C1'].state_machine.transitions[0]
            >>> t2 = a.components['C3'].state_machine.transitions[0]
            >>> tree1 = checkmate.runs.TransitionTree(t1)
            >>> tree2 = checkmate.runs.TransitionTree(t2)
            >>> tree1.match_parent(tree2)
            True
            >>> tree2.match_parent(tree1)
            False
        """
        if len(self.root.outgoing) == 0 or len(tree.root.incoming) == 0:
            return False
        action_code = tree.root.incoming[0].code
        for _o in self.root.outgoing:
            if _o.code == action_code:
                return True
        return False

    def get_node_from_incoming(self, incoming):
        if self.root.incoming and self.root.incoming[0].code == incoming.code:
            return self
        else:
            for _n in self.nodes:
                node = _n.get_node_from_incoming(incoming)
                if node:
                    return node


class RunCollection(list):
    def get_origin_transition(self):
        """
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> src = checkmate.runs.RunCollection()
            >>> src.get_runs_from_application(sample_app.application.TestData())
            >>> [_t.outgoing[0].code for _t in src.origin_transitions]
            ['PBAC', 'PBRL', 'PBPP']
        """
        origin_transitions = []
        for _component in self.application.components.values():
            for _transition in _component.state_machine.transitions:
                if not len(_transition.incoming):
                    origin_transitions.append(_transition)
        return origin_transitions

    @checkmate.fix_issue('checkmate/issues/match_R2_in_runs.rst')
    @checkmate.fix_issue('checkmate/issues/sandbox_runcollection.rst')
    def get_runs_from_application(self, application):
        self.clear()
        self.application = type(application)()
        self.application.start(default_state_value=False)
        self.origin_transitions = self.get_origin_transition()
        for _o in self.origin_transitions:
            sandbox = checkmate.sandbox.CollectionSandbox(self.application)
            for split, _t in sandbox(_o):
                self.append(_t)
