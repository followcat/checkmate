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

    def copy(self, exclude_nodes=None):
        """
            >>> t = Tree('archer', [])
            >>> t.add_node(Tree('captain', [Tree('marshal', [])]))
            >>> t.add_node(Tree('hero', [Tree('champion', [])]))
            >>> t2 = t.copy()
            >>> t2.root
            'archer'
            >>> t2.nodes[0].nodes[0].root
            'marshal'
            >>> t3 = t.copy([t.nodes[0]])
            >>> len(t3.nodes)
            1
            >>> t3.nodes[0].nodes[0].root
            'champion'
        """
        if exclude_nodes is None:
            exclude_nodes = []
        _copy = self.__class__(self.root, [])
        for _node in self.nodes:
            if _node in exclude_nodes:
                exclude_nodes.remove(_node)
                continue
            _copy.nodes.append(_node.copy(exclude_nodes))
        return _copy

    def walk(self):
        """
            visit the tree by depth, and return a list of all nodes
            >>> t = Tree('peasant', [])
            >>> t.add_node(Tree('spearman', []))
            >>> t.add_node(Tree('bowman', []))
            >>> t.nodes[0].add_node(Tree('swordman', []))
            >>> t.nodes[1].add_node(Tree('longbowman', []))
            >>> nodes = t.walk()
            >>> for _node in nodes:
            ...     print(_node)
            peasant
            spearman
            swordman
            bowman
            longbowman
        """

        def re_walk(current_node, return_list=[]):
            return_list.append(current_node.root)
            for _node in current_node.nodes:
                re_walk(_node, return_list)
            return return_list
        return_list = re_walk(self)
        return return_list

    def visual_dump(self):
        d = {}
        d['root'] = self.root.__str__()
        d['nodes'] = []
        for element in self.nodes:
            d['nodes'].append(element.visual_dump())
        return d

    def show_buffer(self, level=0):
        """
            >>> import checkmate._tree
            >>> t = checkmate._tree.Tree('archer', [checkmate._tree.Tree('captain', [checkmate._tree.Tree('marshal', [])]), checkmate._tree.Tree('hero', [checkmate._tree.Tree('champion', [])])])
            >>> t.show_buffer()
            '|archer\\n|     |___ captain\\n|          |___ marshal\\n|     |___ hero\\n|          |___ champion\\n'
            >>> print(t.show_buffer())
            |archer
            |     |___ captain
            |          |___ marshal
            |     |___ hero
            |          |___ champion
            <BLANKLINE>
        """
        visual_dump = self.visual_dump()
        string = "{0}{1}{2}\n".format('|' + ' ' * 5 * level, '|___ ' * bool(level), visual_dump['root'])
        for element in self.nodes:
            string += element.show_buffer(level + 1)
        return string
