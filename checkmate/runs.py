# This code is part of the checkmate project.
# Copyright (C) 2013-2015 The checkmate project contributors
#
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

import copy

import checkmate._tree
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
    """"""
    def get_origin_transition(self, application):
        """
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> transitions = checkmate.runs.RunCollection()
            >>> transitions.get_origin_transition(sample_app.application.TestData())
            >>> [_t.root.outgoing[0].code for _t in transitions]
            ['PBAC', 'PBRL', 'PBPP']
        """
        self.clear()
        for _component in application.components.values():
            for _transition in _component.state_machine.transitions:
                if not len(_transition.incoming):
                    _tree = TransitionTree(_transition)
                    self.append(_tree)

    def build_trees_from_application(self, application):
        """
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> runs = checkmate.runs.RunCollection()
            >>> runs.build_trees_from_application(sample_app.application.TestData())
            >>> len(runs)
            4
            >>> run_length = [len(_run.walk()) for _run in runs]
            >>> run_length.sort()
            >>> run_length
            [5, 6, 6, 9]
            >>> sorted([_t.incoming[0].code for _t in runs.get_runs_from_code('PBRL')[0].walk() if len(_t.incoming) > 0])
            ['DR', 'PBRL', 'RL', 'VODR']
            >>> sorted([_t.incoming[0].code for _t in runs.get_runs_from_code('PBPP')[0].walk() if len(_t.incoming) > 0])
            ['PA', 'PA', 'PBPP', 'PP', 'VOPA']
            >>> sorted([_t.incoming[0].code for _t in runs.get_runs_from_code('OK')[0].walk() if len(_t.incoming) > 0])
            ['AC', 'AP', 'ARE', 'DA', 'OK', 'PBAC', 'RE', 'VODA']
            >>> sorted([_t.incoming[0].code for _t in runs.get_runs_from_code('ER')[0].walk() if len(_t.incoming) > 0])
            ['AC', 'ER', 'PBAC', 'RE', 'VOER']

        """
        self.clear()
        for _component in application.components.values():
            for _transition in _component.state_machine.transitions:
                _tree = TransitionTree(_transition)
                for _i in _tree.root.incoming:
                    for _t in self.get_runs_from_code(_i.code):
                        for _o in _tree.root.outgoing:
                            add_node = _t.get_node_from_incoming(_o)
                            if add_node:
                                _tree.nodes.append(add_node)
                self._add_tree(_tree)
        self.add_return_code_run()

    def add_return_code_run(self):
        """
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> run = checkmate.runs.RunCollection()
            >>> a = sample_app.application.TestData()
            >>> tree0 = checkmate.runs.TransitionTree(a.components['C2'].state_machine.transitions[0])
            >>> tree1 = checkmate.runs.TransitionTree(a.components['C1'].state_machine.transitions[0])
            >>> tree2 = checkmate.runs.TransitionTree(a.components['C1'].state_machine.transitions[3])
            >>> (tree0.root.incoming[0].code, tree1.root.incoming[0].code, tree2.root.incoming[0].code, tree1.root.outgoing[1].code, tree2.root.outgoing[1].code)
            ('PBAC', 'AC', 'AC', 'OK', 'ER')
            >>> run._add_tree(tree0)
            >>> run._add_tree(tree1)
            >>> run._add_tree(tree2)
            >>> len(run)
            1
            >>> len(run[0].nodes)
            2
            >>> run.add_return_code_run()
            >>> len(run)
            2
            >>> len(run[0].nodes), len(run[1].nodes)
            (1, 1)
            >>> [run[0].nodes[0].root.outgoing[1].code, run[1].nodes[0].root.outgoing[1].code]
            ['OK', 'ER']
        """
        return_code_node_list = list()
        append_runs = []

        def walk_find(current_node):
            check_return_code_run(current_node)
            for _node in current_node.nodes:
                walk_find(_node)

        def check_return_code_run(tree):
            set_list = []
            return_code_node_set = set()
            for node in tree.nodes:
                node_set = set([_i.interface for _i in node.root.initial])
                set_list.append(node_set)
            for index, compare_set in enumerate(set_list):
                for _s in set_list:
                    if compare_set is _s:
                        continue
                    if len(compare_set & _s):
                        return_code_node_set.add(tree.nodes[index])
            if len(return_code_node_set):
                return_code_node_list.append(list(return_code_node_set))

        def walk_process(run, current_node, process):
            if process[0] in current_node.nodes:
                for _p in process:
                    temp_process = copy.copy(process)
                    temp_process.remove(_p)
                    append_runs.append(run.copy(temp_process))
                return True
            for _node in current_node.nodes:
                return walk_process(run, _node, process)

        for _r in self:
            return_code_node_list.clear()
            walk_find(_r)
            for _process in return_code_node_list:
                if walk_process(_r, _r, _process):
                    self.remove(_r)
        self.extend(append_runs)
        #FIXME this is required to have runs sorted
        def _ugly_sort_function(x):
            """tree building should be done by keeping order"""
            if len(x.nodes[0].nodes) == 0:
                #required by above function doctest 
                return x.nodes[0].root.outgoing[1].code
            elif len(x.nodes[0].nodes[0].root.outgoing) < 2:
                return x.nodes[0].root.outgoing[0].code
            else:
                return x.nodes[0].nodes[0].root.outgoing[1].code
        self.sort(key=lambda x:_ugly_sort_function(x), reverse=True)

    def get_runs_from_code(self, code):
        """
            >>> import checkmate.runs
            >>> import sample_app.application
            >>> runs = checkmate.runs.RunCollection()
            >>> runs.build_trees_from_application(sample_app.application.TestData())
            >>> runs.get_runs_from_code('PBRL')[0].root.outgoing[0].code
            'PBRL'
        """
        results = []
        for _r in self:
            transitions = _r.walk()
            for _t in transitions:
                if code in [_i.code for _i in _t.incoming + _t.outgoing]:
                    results.append(_r)
                    break
        return results

    def _add_tree(self, des_tree):
        """
            >>> import sample_app.application
            >>> run = checkmate.runs.RunCollection()
            >>> a = sample_app.application.TestData()
            >>> tree1 = checkmate.runs.TransitionTree(a.components['C1'].state_machine.transitions[0])
            >>> tree2 = checkmate.runs.TransitionTree(a.components['C3'].state_machine.transitions[0])
            >>> tree3 = checkmate.runs.TransitionTree(a.components['C2'].state_machine.transitions[2])
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
            if _tree.merge(des_tree):
                is_merged = True
            if des_tree.merge(_tree):
                self.remove(_tree)
                _index -= 1
            _index += 1
        if not is_merged and des_tree not in self:
            self.append(des_tree)
