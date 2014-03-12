import treelib


class NewTree(treelib.Tree):
    def __init__(self, *args, **kwargs):
        super(NewTree,self).__init__(*args, **kwargs)

    def get_root_parent(self, root_nid):
        """
            >>> import checkmate._newtree
            >>> test_tree = checkmate._newtree.NewTree()
            >>> test_tree.create_node('exchange(AC)','AC') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> test_tree.create_node('exchange(RE)','RE',parent='AC') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> test_tree.create_node('exchange(ARE)','ARE',parent='AC') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> print(test_tree.get_root_parent('AP'))
            None
            >>> test_tree.get_root_parent('ARE')
            'ARE'
        """
        son_node = self.get_node(root_nid)
        if son_node and son_node.is_leaf():
            return son_node.identifier
        else:
            return None

    def paste_tree_replace_node(self, pasted_tree, node_tag):
        """
            >>> import checkmate._newtree
            >>> tree_father = checkmate._newtree.NewTree()
            >>> tree_father.create_node('exchange(AC)','AC') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_father.create_node('exchange(RE)','RE',parent='AC') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_father.create_node('exchange(ARE)','ARE',parent='AC') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_child = checkmate._newtree.NewTree()
            >>> tree_child.create_node('exchange(ARE)','ARE') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_child.create_node('exchange(AP)','AP',parent='ARE') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_father.paste_tree_replace_node(tree_child,node_tag='ARE')
            >>> tree_father.showid()
            AC
            |___ ARE
            |    |___ AP
            |___ RE
        """
        parent_tag = self.parent(node_tag).identifier
        self.remove_node(node_tag)
        self.paste(parent_tag, pasted_tree)

    def create_node(self, tag=None, identifier=None, parent=None):
        node = NewNode(tag, identifier)
        self.add_node(node, parent)
        return node

    def merge(self, des_tree):
        #root always incoming
        #node always outgoing
        found = False
        leaf_nid = self.get_root_parent(des_tree.root)
        if leaf_nid is not None:
            found = True
            self.paste_tree_replace_node(des_tree,leaf_nid)
            des_tree = self
        elif des_tree.get_root_parent(self.root) is not None:
            leaf_nid = des_tree.get_root_parent(self.root)
            found = True
            des_tree.paste_tree_replace_node(self,leaf_nid)
        return found, des_tree

    def showid(self, nid=None, level=treelib.Tree.ROOT, idhidden=True, filter=None, key=None, reverse=False):
        save_get_tag = NewNode.get_tag
        NewNode.get_tag = NewNode.identifier
        self.show(nid, level, idhidden, filter, key, reverse)
        NewNode.get_tag = save_get_tag

class NewNode(treelib.Node):
    """"""
    def __init__(self, tag=None, identifier=None, expanded=True):
        super(NewNode,self).__init__(tag=tag,identifier=identifier,expanded=expanded)
        if tag is not None:
            self._tag = tag

    @property
    def tag(self):
        if callable(self.get_tag):
            return self.get_tag()
        else:
            return self.get_tag

    def get_tag(self):
        return self._tag

    def __lt__(self, other):
        return True
