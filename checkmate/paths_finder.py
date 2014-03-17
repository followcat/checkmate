import checkmate._newtree
import checkmate.run_transition


class TransitionTree(checkmate._newtree.NewTree):
    """"""
    def __init__(self, transition):
        """
            >>> import checkmate._storage
            >>> import checkmate.transition
            >>> import checkmate.test_data
            >>> import checkmate.paths_finder
            >>> import sample_app.data_structure
            >>> incoming_list = [checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'AC', None, sample_app.data_structure.ActionPriority)]
            >>> outgoing_list = [checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'RE', None, sample_app.data_structure.ActionPriority), checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'ARE', None, sample_app.data_structure.ActionPriority)]
            >>> test_transition = checkmate.transition.Transition(incoming = incoming_list, outgoing = outgoing_list)
            >>> checkmate.paths_finder.TransitionTree(test_transition).showid()
            AC
            |___ ARE
            |___ RE
        """
        super().__init__()
        incoming_list = transition.incoming
        outgoing_list = transition.outgoing
        if len(incoming_list) == 0:
            return
        self.create_node(transition, incoming_list[0].code)
        for _outgoing in outgoing_list:
            self.create_node(None, _outgoing.code, parent=incoming_list[0].code)


class RunCollection(list):
    def build_trees_from_application(self, application_class):
        """
            >>> import sample_app.application
            >>> import checkmate.paths_finder
            >>> runs = checkmate.paths_finder.RunCollection()
            >>> runs.build_trees_from_application(sample_app.application.TestData)
            >>> len(runs)
            3
        """
        application = application_class()
        for _k, _v in application.components.items():
            for _t in _v.state_machine.transitions:
                if len(_t.incoming) == 0:
                    continue
                temp_tree = TransitionTree(_t)
                if self.merge_tree(temp_tree) == False:
                    self.append(temp_tree)

    def merge_tree(self, des_tree):
        """
            >>> import sample_app.application
            >>> import checkmate.paths_finder
            >>> r = checkmate.paths_finder.RunCollection()
            >>> tree_one = checkmate._newtree.NewTree()
            >>> tree_one.create_node(sample_app.application.TestData().components['C1'].state_machine.transitions[0], 'AC') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_one.add_node(checkmate._newtree.NewNode(None, 'RE'), parent='AC')
            >>> tree_one.add_node(checkmate._newtree.NewNode(None, 'ARE'), parent='AC')
            >>> if r.merge_tree(tree_one) == False:
            ...        r.append(tree_one)
            >>> r[0].showid()
            AC
            |___ ARE
            |___ RE
            >>> tree_two = checkmate._newtree.NewTree()
            >>> tree_two.create_node(sample_app.application.TestData().components['C2'].state_machine.transitions[1], 'ARE') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_two.add_node(checkmate._newtree.NewNode(None, 'AP'), parent='ARE')
            >>> tree_two.showid()
            ARE
            |___ AP
            >>> r.merge_tree(tree_two)
            True
            >>> r[0].showid()
            AC
            |___ ARE
            |    |___ AP
            |___ RE
            >>> tree = r[0]
            >>> [tree.get_node(n)._tag for n in tree.get_node(tree.root).fpointer] # doctest: +ELLIPSIS
            [None, <checkmate.transition.Transition object at ...
        """
        found = False
        once_found = False
        for _tree in self[:]:
            found, des_tree = _tree.merge(des_tree)
            if found:
                once_found = True
                self.remove(_tree)
        if once_found:
            self.append(des_tree)
            self.merge_tree(des_tree)
        return once_found

class HumanInterfaceExchangesFinder(object):
    def __init__(self, application_class):
        """
            >>> import sample_app.application
            >>> import checkmate.paths_finder
            >>> hi = checkmate.paths_finder.HumanInterfaceExchangesFinder(sample_app.application.TestData)
            >>> hi.human_interface_exchange_code_list
            ['AC', 'RL', 'PP']
        """
        self.transition_list = []
        self.human_interface_exchange_code_list = []
        self.application = application_class()
        self.get_Importent_Exchange_from_application()

    def get_Importent_Exchange_from_application(self):
        for _k, _v in self.application.components.items():
            self.transition_list.extend(_v.state_machine.transitions)
        for _t in self.transition_list:
            if len(_t.incoming) == 0 and len(_t.outgoing) > 0:
                for _outgoing in _t.outgoing:
                    self.human_interface_exchange_code_list.append(_outgoing.code)

class PathBuilder(object):
    def __init__(self, application_class):
        self.path_list = []
        self.application_class = application_class
        self.tree_list = RunCollection()
        self.tree_list.build_trees_from_application(application_class)

    def make_path(self, unprocessed = None, unprocessed_initial_state = None):
        """
            >>> import sample_app.application
            >>> import checkmate.paths_finder
            >>> pb = checkmate.paths_finder.PathBuilder(sample_app.application.TestData)
        """
        if unprocessed is None:
            unprocessed = self.tree_list
        found = False
        for _i in range(len(unprocessed)):
            found = False
            process_exchange_list = [unprocessed[_i][_node].tag for _node in unprocessed[_i].expand_tree(mode=checkmate._newtree.NewTree.ZIGZAG)]
            temp_transition = checkmate.run_transition.get_transition(self.application_class,process_exchange_list, unprocessed_initial_state[_i])
            if temp_transition is not None:
                self.path_list.append([temp_transition])
                found = True
            else:
                for _path in self.path_list:
                    if len(unprocessed) <= 0:
                        break
                    temp_transition = checkmate.run_transition.get_transition(self.application_class, process_exchange_list, unprocessed_initial_state[_i], _path)
                    if temp_transition is not None:
                        new_path = _path[0:_path.index(temp_transition.previous_transitions[0])+1]
                        new_path.append(temp_transition)
                        #replace the current path with newer longer one
                        if len(new_path) > len(_path):
                            self.path_list.remove(_path)
                        self.path_list.append(new_path)
                        found = True
                for _p in self.path_list:
                    for _s in _p:
                        if _s.is_matching_final(temp_transition.initial) and temp_transition not in _s.previous_transitions:
                            _s.next_transitions.append(temp_transition)
                        if _s.is_matching_initial(temp_transition.final) and temp_transition not in _s.next_transitions:
                            _s.previous_transitions.append(temp_transition)
            if found:
                unprocessed.remove(unprocessed[_i])
                self.make_path(unprocessed, unprocessed_initial_state)
                break 
