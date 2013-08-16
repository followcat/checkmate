import zope.interface


class ITree(zope.interface.Interface):
    """"""


@zope.interface.implementer(ITree)
class Tree(object):
    def __init__(self, root, _nodes=[]):
        for node in _nodes:
            assert ITree.providedBy(node)
        self.root = root
        self.nodes = _nodes

    def add_node(self, tree):
        assert ITree.providedBy(tree)
        self.nodes.append(tree)

