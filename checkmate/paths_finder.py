import checkmate._newtree
import checkmate.run_transition


class ExchangeTreesFinder(object):
    def __init__(self, application_class):
        """
            >>> import sample_app.application
            >>> import checkmate.paths_finder
            >>> etf = checkmate.paths_finder.ExchangeTreesFinder(sample_app.application.TestData)
            >>> len(etf.trees)
            3
        """
        self.trees = []
        self.transition_list = []
        self.trees_initial_list = []
        self.application = application_class()
        self.application_class = application_class
        self.build_trees_from_application()
        self.build_trees_initial_state_list()

    def build_trees_from_application(self):
        self.transition_list = []
        for _k,_v in self.application.components.items(): 
            self.transition_list .extend(_v.state_machine.transitions)
        for _t in self.transition_list :
            temp_tree = self.get_transition_tree(_t)
            if temp_tree is None:
                continue
            if self.merge_tree(temp_tree) == False:
                self.trees.append(temp_tree)

    def build_trees_initial_state_list(self):
        for _tree in self.trees:
            temp_initial_state_list = []
            for _nodeid in _tree.expand_tree(mode=checkmate._newtree.NewTree.ZIGZAG):
                for _t_init in [_t.initial for _t in self.transition_list if len(_t.incoming) > 0 and  _t.incoming[0].code == _nodeid]:
                    for _each_t_init in _t_init: 
                        if _each_t_init.code not in [_temp_init.code for _temp_init in temp_initial_state_list] :
                            temp_initial_state_list.append(_each_t_init)
            self.trees_initial_list.append(temp_initial_state_list)

    def get_transition_tree(self, transition):
        """
            >>> import checkmate._storage
            >>> import checkmate.transition
            >>> import checkmate.test_data
            >>> import checkmate.paths_finder
            >>> import sample_app.data_structure
            >>> r = checkmate.paths_finder.ExchangeTreesFinder(checkmate.test_data.App)
            >>> incoming_list = [checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'AC', None, sample_app.data_structure.ActionPriority)]
            >>> outgoing_list = [checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'RE', None, sample_app.data_structure.ActionPriority),checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'ARE', None, sample_app.data_structure.ActionPriority)]
            >>> test_transition = checkmate.transition.Transition(incoming = incoming_list,outgoing = outgoing_list)
            >>> r.get_transition_tree(test_transition).showid()
            AC
            |___ ARE
            |___ RE
        """
        incoming_list = transition.incoming
        outgoing_list = transition.outgoing
        if len(incoming_list) == 0 or len(outgoing_list) == 0:
            return None
        build_tree = checkmate._newtree.NewTree()
        build_tree.create_node(getattr(self.application.exchange_module, incoming_list[0].code)(),incoming_list[0].code)
        for outgoing in outgoing_list:
            build_tree.create_node(getattr(self.application.exchange_module, outgoing.code)(), outgoing.code,parent=incoming_list[0].code)
        return build_tree

    def merge_tree(self, des_tree):
        """
            >>> import sample_app.application
            >>> import checkmate.paths_finder
            >>> r = checkmate.paths_finder.ExchangeTreesFinder(sample_app.application.TestData)
            >>> tree_one = checkmate._newtree.NewTree()
            >>> tree_one.create_node('exchange(AC)','AC') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_one.add_node(checkmate._newtree.NewNode('exchange(RE)','RE'),parent='AC')
            >>> tree_one.add_node(checkmate._newtree.NewNode('exchange(ARE)','ARE'),parent='AC')
            >>> r.trees = []
            >>> if r.merge_tree(tree_one) == False:
            ...        r.trees.append(tree_one)
            >>> r.trees[0].showid()
            AC
            |___ ARE
            |___ RE
            >>> tree_two = checkmate._newtree.NewTree()
            >>> tree_two.create_node('exchange(ARE)','ARE') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_two.add_node(checkmate._newtree.NewNode('exchange(AP)','AP'),parent='ARE')
            >>> tree_two.showid()
            ARE
            |___ AP
            >>> r.merge_tree(tree_two)
            True
            >>> r.trees[0].showid()
            AC
            |___ ARE
            |    |___ AP
            |___ RE
        """
        #root always incoming
        #node always outgoing
        found = False
        for _tree in self.trees[:]:
            leaf_nid = _tree.get_root_parent(des_tree.root)
            if leaf_nid is not None:
                found = True
                _tree.paste_tree_replace_node(des_tree,leaf_nid)
                self.trees.remove(_tree)
                des_tree = _tree
            leaf_nid = des_tree.get_root_parent(_tree.root)
            if leaf_nid is not None:
                found = True
                des_tree.paste_tree_replace_node(_tree,leaf_nid)
                self.trees.remove(_tree)
        if found:
            self.trees.append(des_tree)
            self.merge_tree(des_tree)
        return found

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
        for _k,_v in self.application.components.items(): 
            self.transition_list.extend(_v.state_machine.transitions)
        for _t in self.transition_list:
            if len(_t.incoming) == 0 and len(_t.outgoing) > 0:
                for _outgoing in _t.outgoing:
                    self.human_interface_exchange_code_list.append(_outgoing.code)

class PathBuilder(object):
    def __init__(self, exchange_trees_finder):
        self.tree_list = exchange_trees_finder.trees
        self.init_state_list = exchange_trees_finder.trees_initial_list
        self.application_class = exchange_trees_finder.application_class
        self.path_list = []

    def make_path(self, unprocessed = None, unprocessed_initial_state = None):
        """
            >>> import sample_app.application
            >>> import checkmate.paths_finder
            >>> etf = checkmate.paths_finder.ExchangeTreesFinder(sample_app.application.TestData)
            >>> pb = checkmate.paths_finder.PathBuilder(etf)
            >>> pb.make_path()
            >>> for _path in pb.path_list:
            ...      for _step in _path:
            ...         for _initstate in _step.initial:
            ...             if _initstate.partition_id == "S-ACK-01" or _initstate.partition_id == "S-ACK-02":
            ...                 print(_initstate.partition_id,_initstate.value)
            ...         print("|")
            ...         for _finalstate in _step.final:
            ...             if _finalstate.partition_id == "S-ACK-01" or _finalstate.partition_id == "S-ACK-02":
            ...                 print(_finalstate.partition_id,_finalstate.value)
            ...         print("-------------------------")
            S-ACK-01 False
            |
            S-ACK-02 True
            -------------------------
            S-ACK-02 True
            |
            S-ACK-01 False
            -------------------------
            S-ACK-01 False
            |
            S-ACK-01 False
            -------------------------
        """
        if unprocessed is None:
            unprocessed = self.tree_list
        if unprocessed_initial_state is None:
            unprocessed_initial_state = self.init_state_list
        found = False
        for _i in range(len(unprocessed)):
            found = False
            process_exchange_list = [unprocessed[_i][_node].tag for _node in unprocessed[_i].expand_tree(mode=checkmate._newtree.NewTree.ZIGZAG)]
            temp_transitions = checkmate.run_transition.get_transition_list(self.application_class,process_exchange_list,unprocessed_initial_state[_i])
            if temp_transitions is not None:
                self.path_list.append(temp_transitions)
                found = True
            else:
                for _path in self.path_list:
                    if len(unprocessed) <= 0:
                        break
                    temp_transitions = checkmate.run_transition.get_transition_list(self.application_class,process_exchange_list,unprocessed_initial_state[_i],_path)
                    if temp_transitions is not None:
                        #replace the current path with newer longer one
                        if len(temp_transitions) > len(_path):
                            self.path_list.remove(_path)
                        self.path_list.append(temp_transitions)
                        found = True
            if found:
                unprocessed.remove(unprocessed[_i])
                unprocessed_initial_state.remove(unprocessed_initial_state[_i])
                self.make_path(unprocessed,unprocessed_initial_state)
                break 
