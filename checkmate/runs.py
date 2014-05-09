import checkmate._tree
import checkmate.transition


class TransitionTree(checkmate._tree.Tree):
    """"""
    def __init__(self, transition):
        """
            >>> import checkmate._storage
            >>> import checkmate.transition
            >>> import sample_app.application
            >>> import sample_app.data_structure
            >>> incoming_list = [checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'AC', None, sample_app.data_structure.ActionPriority)]
            >>> outgoing_list = [checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'RE', None, sample_app.data_structure.ActionPriority), checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'ARE', None, sample_app.data_structure.ActionPriority)]
            >>> test_transition = checkmate.transition.Transition(incoming = incoming_list, outgoing = outgoing_list)
            >>> tree = checkmate.runs.TransitionTree(test_transition)
            >>> (tree.root.incoming[0].code, tree.root.outgoing[0].code, tree.root.outgoing[1].code)
            ('AC', 'RE', 'ARE')
            >>> tt = checkmate.runs.TransitionTree(sample_app.application.TestData().components['C1'].state_machine.transitions[0])
            >>> tt.root #doctest: +ELLIPSIS
            <checkmate.transition.Transition object at ...
        """
        assert type(transition) == checkmate.transition.Transition
        super(TransitionTree, self).__init__(transition, [])

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
        for node in self.nodes:
            if node.merge(tree):
                return True

    def match_parent(self, tree):
        """
        """
        if len(self.root.outgoing) == 0 or len(tree.root.incoming) == 0:
            return False
        action_code = tree.root.incoming[0].code
        for _o in self.root.outgoing:
            if _o.code == action_code:
                return True
        return False

class RunCollection(list):
    def build_trees_from_application(self, application):
        """
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> runs = checkmate.runs.RunCollection()
            >>> runs.build_trees_from_application(sample_app.application.TestData())
            >>> len(runs)
            3
            >>> for _run in runs:
            ...     len(_run.walk())
            8
            5
            6
            >>> [run.incoming[0].code for run in runs[1].walk() if len(run.incoming) > 0]
            ['PBRL', 'RL', 'DR', 'VODR']

        """
        for _component in application.components.values():
            for _transition in _component.state_machine.transitions:
                _tree = TransitionTree(_transition)
                self._add_tree(_tree)

    def _add_tree(self, des_tree):
        """
            >>> import sample_app.application
            >>> run = checkmate.runs.RunCollection()
            >>> a = sample_app.application.TestData()
            >>> tree1 = checkmate.runs.TransitionTree(a.components['C1'].state_machine.transitions[0])
            >>> tree2 = checkmate.runs.TransitionTree(a.components['C3'].state_machine.transitions[0])
            >>> tree3 = checkmate.runs.TransitionTree(a.components['C2'].state_machine.transitions[1])
            >>> (tree1.root.incoming[0].code, tree2.root.incoming[0].code, tree3.root.incoming[0].code)
            ('AC', 'RE', 'ARE')
            >>> run._add_tree(tree1)
            >>> run._add_tree(tree2)
            >>> run._add_tree(tree3)
            >>> len(run)
            1
            >>> tree2 in tree1.nodes, tree3 in tree1.nodes 
            (True, True)
        """
        is_merged = False
        _index = 0
        while _index < len(self):
            _tree = self[_index]
            if not is_merged and _tree.merge(des_tree):
                is_merged = True
            if des_tree.merge(_tree):
                self.remove(_tree)
                _index -= 1
            _index += 1
        if not is_merged and des_tree not in self:
            self.append(des_tree)

