import treelib

class RunsFinder(object):
    def __init__(self,application):
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

    def get_transition_tree(self,transition):
            incomming_list = transition.incoming
            outgoing_list = transition.outgoing
            if len(incomming_list) == 0 or len(outgoing_list) == 0:
                return None
            build_tree = treelib.Tree()
            build_tree.create_node(incomming_list[0].code,incomming_list[0].code)
            for outgoing in outgoing_list:
                outgoing_node = treelib.Node(outgoing.code, outgoing.code)
                build_tree.add_node(outgoing_node,parent=incomming_list[0].code)
            return build_tree

    def get_root_parent(self,tree,root_nid):
        son_node = tree.get_node(root_nid)
        if son_node and son_node.is_leaf():
            return son_node.identifier
        else:
            return None

    def paste_tree_replace_node(self,tree,pasted_tree,node_tag):
        parent_tag = tree.parent(node_tag).identifier
        tree.remove_node(node_tag)
        tree.paste(parent_tag, pasted_tree)

    def merge_tree(self,des_tree):
        #root always incoming
        #node always outgoing
        #get_root_parent is check one incoming is someone's outgoing,and return that one incoming code
        found = False
        for _tree in self.trees[:]:
            leaf_nid = self.get_root_parent(_tree,des_tree.root)
            if leaf_nid is not None:
                found = True
                self.paste_tree_replace_node(_tree,des_tree,leaf_nid)
                self.trees.remove(_tree)
                des_tree = _tree
            leaf_nid = self.get_root_parent(des_tree,_tree.root)
            if leaf_nid is not None:
                found = True
                self.paste_tree_replace_node(des_tree,_tree,leaf_nid)
                self.trees.remove(_tree)
        if found:
            self.trees.append(des_tree)
            self.merge_tree(des_tree)
        return found

class ImportentExchangeFinder(object):
    def __init__(self,application):
        self.importent_exchange = []
        self.application = application
        self.get_Importent_Exchange_from_application()

    def get_Importent_Exchange_from_application(self):
        transition_list = []
        for _k,_v in self.application.components.items(): 
            transition_list.extend(_v.state_machine.transitions)
        for _t in transition_list:
            if len(_t.incoming) == 0 and len(_t.outgoing) > 0:
                self.importent_exchange.append(_t.outgoing[0].code)



def main():
    import sample_app.application
    import checkmate.component

    a = sample_app.application.TestData()
    r = RunsFinder(a)
    for each in r.trees:
        each.show()
        print('---------------')

    a2 = sample_app.application.TestData()
    i = ImportentExchangeFinder(a2)
    for each in i.importent_exchange:
        print(each)

if __name__ == '__main__':
    main()