# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.types import Undefined

try:
    from mptt.models import (
        MPTTModel,
        MPTTModelBase as NestableBase,
        TreeForeignKey as ParentForeignKey)
except ImportError:
    __all__ = ()
else:
    __all__ = ('Nestable', 'NestableBase', 'ParentForeignKey')


    class Nestable(MPTTModel):

        class Meta:
            abstract = True

        _ancestors = Undefined
        _children = Undefined
        _descendants = Undefined
        _root = Undefined
        _siblings = Undefined

        def get_ancestors(self, ascending=False, include_self=False):
            if self._ancestors is Undefined:
                qs = self.get_ancestors_queryset()
                self._ancestors = list(qs.iterator())

            ancestors = self._ancestors[:]
            if include_self:
                ancestors.append(self)
            if ascending:
                ancestors.reverse()
            return ancestors

        def get_ancestors_queryset(self, ascending=False, include_self=False):
            return super(Nestable, self).get_ancestors(ascending, include_self)

        def get_children(self):
            if self._children is Undefined:
                qs = self.get_children_queryset()
                self._children = list(qs.iterator())

            return self._children[:]

        def get_children_queryset(self):
            return super(Nestable, self).get_children()

        def get_descendants(self, include_self=False):
            if self._descendants is Undefined:
                qs = self.get_descendants_queryset()
                self._descendants = list(qs.iterator())

            descendants = self._descendants[:]
            if include_self:
                descendants[0:0] = [self]
            return descendants

        def get_descendants_queryset(self, include_self=False):
            return super(Nestable, self).get_descendants(include_self)

        def get_parent(self):
            return getattr(self, self._mptt_meta.parent_attr)

        def get_root(self):
            if self._root is Undefined:
                self._root = super(Nestable, self).get_root()

            return self._root

        def get_siblings(self, include_self=False):
            if self._siblings is Undefined:
                qs = self.get_siblings_queryset()
                self._siblings = list(qs.iterator())

            siblings = self._siblings[:]
            if include_self:
                if self.is_root_node():
                    tree_attr = self._mptt_meta.tree_id_attr

                    self_tree = getattr(self, tree_attr)
                    for i, node in enumerate(siblings):
                        if getattr(node, tree_attr) > self_tree:
                            siblings.insert(i, self)
                            break
                    else:
                        siblings.append(self)
                else:
                    left_attr = self._mptt_meta.left_attr
                    right_attr = self._mptt_meta.right_attr

                    self_right = getattr(self, right_attr)
                    for i, node in enumerate(siblings):
                        if getattr(node, left_attr) == self_right:
                            siblings.insert(i, self)
                            break
                    else:
                        siblings.append(self)

            return siblings

        def get_siblings_queryset(self, include_self=False):
            return super(Nestable, self).get_siblings(include_self)

