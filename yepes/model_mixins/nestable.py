# -*- coding:utf-8 -*-

from __future__ import unicode_literals

try:
    import mptt
except ImportError:
    __all__ = ()
else:
    from itertools import chain

    from mptt.models import (
        MPTTModel,
        MPTTModelBase as NestableBase,
        raise_if_unsaved,
        TreeForeignKey as ParentForeignKey,
    )

    from yepes.managers import NestableManager, TreeQuerySet
    from yepes.types import Undefined

    __all__ = ('Nestable', 'NestableBase', 'ParentForeignKey')


    class Nestable(MPTTModel):

        objects = NestableManager()

        class Meta:
            abstract = True

        _ancestors = Undefined
        _children = Undefined
        _descendants = Undefined
        _root = Undefined
        _siblings = Undefined
        _subtrees = False

        def _parent_is_cached(self):
            opts = self._mptt_meta
            cache_name = getattr(opts, 'parent_cache_name', Undefined)
            if cache_name is Undefined:
                field_name = opts.parent_attr
                field = self._meta.get_field(field_name)
                opts.parent_cache_name = cache_name = field.get_cache_name()

            return (getattr(self, cache_name, None) is not None)

        @raise_if_unsaved
        def get_ancestors(self, ascending=False, include_self=False):
            if self._ancestors is Undefined:
                node = self
                ancestors = []
                while node._parent_is_cached():
                    node_parent = node.get_parent()
                    if node_parent is None:
                        break

                    node = node_parent
                    ancestors.insert(0, node)

                if node.is_root_node():
                    self._ancestors = ancestors
                else:
                    qs = self.get_ancestors_queryset()
                    if qs._result_cache is None:
                        self._ancestors = list(qs.iterator())
                    else:
                        self._ancestors = qs._result_cache

            ancestors = self._ancestors[:]
            if include_self:
                ancestors.append(self)
            if ascending:
                ancestors.reverse()
            return ancestors

        def get_ancestors_queryset(self, ascending=False, include_self=False):
            return super(Nestable, self).get_ancestors(ascending, include_self)

        @raise_if_unsaved
        def get_children(self):
            if self._children is Undefined:
                qs = self.get_children_queryset()
                if qs._result_cache is None:
                    self._children = list(qs.iterator())
                else:
                    self._children = qs._result_cache

            return self._children[:]

        def get_children_queryset(self):
            qs = super(Nestable, self).get_children()
            if (not self._meta.ordering
                    and self._mptt_meta.order_insertion_by):
                qs = qs.order_by(self._mptt_meta.left_attr)
            return qs

        @raise_if_unsaved
        def get_descendants(self, include_self=False):
            if self._descendants is Undefined:
                qs = self.get_descendants_queryset()
                if qs._result_cache is None:
                    self._descendants = list(qs.iterator())
                else:
                    self._descendants = qs._result_cache

            descendants = self._descendants[:]
            if include_self:
                descendants[0:0] = [self]
            return descendants

        def get_descendants_queryset(self, include_self=False):
            qs = super(Nestable, self).get_descendants(include_self)
            if (not self._meta.ordering
                    and self._mptt_meta.order_insertion_by):
                qs = qs.order_by(self._mptt_meta.left_attr)
            return qs

        @raise_if_unsaved
        def get_parent(self):
            return getattr(self, self._mptt_meta.parent_attr)

        @raise_if_unsaved
        def get_root(self):
            if self._root is Undefined:
                if self._ancestors:
                    self._root = self._ancestors[0]
                else:
                    node = self
                    while node._parent_is_cached():
                        node_parent = node.get_parent()
                        if node_parent is None:
                            break

                        node = node_parent

                    if node.is_root_node():
                        self._root = node
                    else:
                        self._root = super(Nestable, self).get_root()

            return self._root

        @raise_if_unsaved
        def get_siblings(self, include_self=False):
            if self._siblings is Undefined:
                if self.is_child_node() and self._parent_is_cached():
                    # Parent's children nodes could be cached but, if they
                    # are not cached, there is no performance loss because
                    # only one query will be done.
                    level = self.get_parent().get_children()
                    self._siblings = [
                        node
                        for node
                        in level
                        if node.pk != self.pk
                    ]
                else:
                    qs = self.get_siblings_queryset()
                    if qs._result_cache is None:
                        self._siblings = list(qs.iterator())
                    else:
                        self._siblings = qs._result_cache

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
            qs = super(Nestable, self).get_siblings(include_self)
            if (not self._meta.ordering
                    and self._mptt_meta.order_insertion_by):
                qs = qs.order_by(self._mptt_meta.left_attr)
            return qs

        def get_subtrees(self, include_self=False):
            if not self._subtrees:
                qs = self.get_subtrees_queryset()
                qs._fetch_all()
                self._children = qs._result_cache
                self._descendants = qs._nodes_queryset._result_cache
                self._subtrees = True

            if include_self:
                return self
            else:
                return self._children

        def get_subtrees_queryset(self, include_self=False):
            return TreeQuerySet(self.get_descendants_queryset(include_self))

