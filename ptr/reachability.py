# -*- coding: utf-8 -*-
from copy import deepcopy
from pprint import pformat
from collections import deque

class Node(object):
    def __init__(self, net, marking, transition=None, parent=None):
        self.net = net
        self.marking = marking
        self.transition = transition
        self.parent = parent
        self.children = []


    def pformat(self, indent=2):
        return '\n' + pformat([self.transition, self.marking], indent=indent) +\
               '\n'.join((node.pformat(indent+4) for node in self.children))

    @property
    def has_enabled_transitions(self):
        self.__dict__['has_enabled_transitions'] = any([t.enabled(self.marking) for t in self.net.transitions])
        return self.__dict__['has_enabled_transitions']

    @property
    def root_path(self):
        if self.parent:
            self.__dict__['root_path'] = [self.parent,] + self.parent.root_path
        else:
            self.__dict__['root_path'] = []
        return self.__dict__['root_path']

    @property
    def is_attack_ancestor(self):
        self.__dict__['attack_ancestor'] = any((subnode.transition.is_attack for subnode in self.children))
        return self.__dict__['attack_ancestor']

class Graph(object):
    def __init__(self, net, root):
        self.root = Node(net, root)
        self.net = net
        self._leafs = []
        self._non_leafs = []

    def _build_tree(self):
        self._attacks = []
        markings = []
        q = deque((self.root,))
        while q:
            node = q.popleft()
            for transition, marking in self.net.submarkings(node.marking):

                subnode = Node(self.net, marking, transition=transition, parent=node)
                node.children.append(subnode)

                if transition.is_attack:
                    self._attacks.append([subnode,]+subnode.root_path)
                    self._leafs.append(subnode)
                    continue

                if subnode.has_enabled_transitions:

                    if not marking in markings:
                        markings.append(marking)
                    else:
                        self._leafs.append(subnode)
                        continue

                    q.append(subnode)
                    self._non_leafs.append(subnode)
                else:
                    self._leafs.append(subnode)
        self._tree_built = True

    @property
    def attacks(self):
        if not getattr(self, '_tree_built', False):
            self._build_tree()
        return self._attacks

    def format_tree(self):
        return self.root.pformat()

    def render(self, dest):
        pass

    def render_attack(self, path):
        pass