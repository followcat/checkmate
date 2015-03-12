# This code is part of the checkmate project.
# Copyright (C) 2013-2014 The checkmate project contributors
# 
# This program is free software under the terms of the GNU GPL, either
# version 3 of the License, or (at your option) any later version.

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

