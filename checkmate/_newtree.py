import treelib


class NewTree(treelib.Tree):
    def __init__(self, *args, **kwargs):
        super(NewTree,self).__init__(*args, **kwargs)

    def get_root_parent(self, root_nid):
        """
            >>> import checkmate._newtree
            >>> test_tree = checkmate._newtree.NewTree()
            >>> test_tree.create_node('AC','ac') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> test_tree.add_node(treelib.Node('RE','re'),parent='ac')
            >>> test_tree.add_node(treelib.Node('ARE','are'),parent='ac')
            >>> print(test_tree.get_root_parent('ap'))
            None
            >>> test_tree.get_root_parent('are')
            'are'
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
            >>> tree_father.create_node('AC','ac') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_father.add_node(treelib.Node('RE','re'),parent='ac')
            >>> tree_father.add_node(treelib.Node('ARE','are'),parent='ac')
            >>> tree_child = checkmate._newtree.NewTree()
            >>> tree_child.create_node('ARE','are') # doctest: +ELLIPSIS
            <checkmate._newtree.NewNode object at ...
            >>> tree_child.add_node(treelib.Node('AP','ap'),parent='are')
            >>> tree_father.paste_tree_replace_node(tree_child,node_tag='are')
            >>> tree_father.show()
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

class NewNode(treelib.Node):
    """"""
    def __init__(self, tag=None, identifier=None, expanded=True):
        super(NewNode,self).__init__(tag=tag,identifier=identifier,expanded=expanded)
