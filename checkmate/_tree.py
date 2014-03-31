import zope.interface


class ITree(zope.interface.Interface):
    """"""


@zope.interface.implementer(ITree)
class Tree(object):
    def __init__(self, root, _nodes):
        """
            >>> t = Tree('archer', [Tree('captain', [Tree('marshal', [])]), Tree('hero', [Tree('champion', [])])])
            >>> t.nodes[0].nodes[0].root
            'marshal'
            >>> t.nodes[1].nodes[0].root
            'champion'
        """
        assert type(_nodes) is list
        for _node in _nodes:
            assert ITree.providedBy(_node)
        self.root = root
        self.nodes = _nodes

    def add_node(self, tree):
        """
            >>> t = Tree('archer', [])
            >>> t.add_node(Tree('captain', [Tree('marshal', [])]))
            >>> t.add_node(Tree('hero', [Tree('champion', [])]))
            >>> t.nodes[0].nodes[0].root
            'marshal'
            >>> t.nodes[1].nodes[0].root
            'champion'

            >>> t = Tree('peasant', [])
            >>> t.add_node(Tree('spearman', []))
            >>> t.add_node(Tree('bowman', []))
            >>> t.nodes[0].add_node(Tree('swordman', []))
            >>> t.nodes[1].add_node(Tree('longbowman', []))
            >>> t.nodes[0].nodes[0].root
            'swordman'
            >>> t.nodes[1].nodes[0].root
            'longbowman'
        """
        assert ITree.providedBy(tree)
        self.nodes.append(tree)

    def remove_node(self, tree):
        """
            >>> t = Tree('archer', [])
            >>> t2 = Tree('captain', [Tree('marshal', [])])
            >>> t.add_node(t2)
            >>> t.nodes[0].nodes[0].root
            'marshal'
            >>> t.remove_node(t2)
            >>> len(t.nodes)
            0
        """
        assert ITree.providedBy(tree)
        self.nodes.remove(tree)

