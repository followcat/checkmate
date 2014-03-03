import treelib

import checkmate._newtree


class ExchangeTreesFinder(object):
    def __init__(self, application):
        """
            >>> import checkmate.paths_finder
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> etf = checkmate.paths_finder.ExchangeTreesFinder(a)
            >>> len(etf.trees)
            3
        """
        self.trees = []
        self.application = application
        self.build_trees_from_application()

    def build_trees_from_application(self):
        transition_list = []
        for _k,_v in self.application.components.items(): 
            transition_list.extend(_v.state_machine.transitions)
        for _t in transition_list:
            temp_tree = self.get_transition_tree(_t)
            if temp_tree is None:
                continue
            if self.merge_tree(temp_tree) == False:
                self.trees.append(temp_tree)

    def get_transition_tree(self, transition):
        """
            >>> import checkmate._storage
            >>> import checkmate.transition
            >>> import checkmate.test_data
            >>> import checkmate.paths_finder
            >>> import sample_app.data_structure
            >>> a = checkmate.test_data.App()
            >>> r = checkmate.paths_finder.ExchangeTreesFinder(a)
            >>> incoming_list = [checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'AC', None, sample_app.data_structure.ActionPriority)]
            >>> outgoing_list = [checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'RE', None, sample_app.data_structure.ActionPriority),checkmate._storage.InternalStorage(sample_app.data_structure.IActionPriority, 'ARE', None, sample_app.data_structure.ActionPriority)]
            >>> test_transition = checkmate.transition.Transition(incoming = incoming_list,outgoing = outgoing_list)
            >>> r.get_transition_tree(test_transition).show()
            AC
            |___ ARE
            |___ RE
        """
        incomming_list = transition.incoming
        outgoing_list = transition.outgoing
        if len(incomming_list) == 0 or len(outgoing_list) == 0:
            return None
        build_tree = checkmate._newtree.NewTree()
        build_tree.create_node(incomming_list[0].code,incomming_list[0].code)
        for outgoing in outgoing_list:
            outgoing_node = treelib.Node(outgoing.code, outgoing.code)
            build_tree.add_node(outgoing_node,parent=incomming_list[0].code)
        return build_tree

    def merge_tree(self, des_tree):
        """
            >>> import sample_app.application
            >>> import checkmate.paths_finder
            >>> a = sample_app.application.TestData()
            >>> r = checkmate.paths_finder.ExchangeTreesFinder(a)
            >>> tree_one = checkmate._newtree.NewTree()
            >>> tree_one.create_node('AC','ac') # doctest: +ELLIPSIS
            <treelib.node.Node object at ...
            >>> tree_one.add_node(treelib.Node('RE','re'),parent='ac')
            >>> tree_one.add_node(treelib.Node('ARE','are'),parent='ac')
            >>> r.trees = []
            >>> if r.merge_tree(tree_one) == False:
            ...        r.trees.append(tree_one)
            >>> r.trees[0].show()
            AC
            |___ ARE
            |___ RE
            >>> tree_two = checkmate._newtree.NewTree()
            >>> tree_two.create_node('ARE','are') # doctest: +ELLIPSIS
            <treelib.node.Node object at ...
            >>> tree_two.add_node(treelib.Node('AP','ap'),parent='are')
            >>> tree_two.show()
            ARE
            |___ AP
            >>> r.merge_tree(tree_two)
            True
            >>> r.trees[0].show()
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
    def __init__(self, application):
        """
            >>> import checkmate.component
            >>> import checkmate.paths_finder
            >>> import sample_app.application
            >>> a = sample_app.application.TestData()
            >>> hi = checkmate.paths_finder.HumanInterfaceExchangesFinder(a)
            >>> hi.human_interface_exchange_code_list
            ['AC', 'RL', 'PP']
        """
        self.application = application
        self.transition_list = []
        self.human_interface_exchange_code_list = []
        self.get_Importent_Exchange_from_application()

    def get_Importent_Exchange_from_application(self):
        for _k,_v in self.application.components.items(): 
            self.transition_list.extend(_v.state_machine.transitions)
        for _t in self.transition_list:
            if len(_t.incoming) == 0 and len(_t.outgoing) > 0:
                for _outgoing in _t.outgoing:
                    self.human_interface_exchange_code_list.append(_outgoing.code)