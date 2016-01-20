# -*- coding:utf-8 -*-

from __future__ import unicode_literals

try:
    import mptt
except ImportError:
    __all__ = ()
else:
    from copy import deepcopy

    from django.db.models.query import QuerySet, REPR_OUTPUT_SIZE
    from django.utils import six

    from mptt.managers import TreeManager as MPTTManager
    from mptt.querysets import TreeQuerySet as MPTTQuerySet

    from yepes.exceptions import UnexpectedTypeError

    __all__ = ('NestableManager', 'NestableQuerySet', 'TreeQuerySet')


    class TreeQuerySet(object):

        def __init__(self, queryset):
            self._nodes_queryset = queryset
            self._result_cache = None

        def __and__(self, other):
            if isinstance(other, TreeQuerySet):
                return TreeQuerySet(self._nodes_queryset & other._nodes_queryset)
            else:
                return TreeQuerySet(self._nodes_queryset & other)

        def __bool__(self):
            self._fetch_all()
            return bool(self._result_cache)

        __nonzero__ = __bool__    # Python 2 compatibility

        def __deepcopy__(self, memo):
            obj = self.__class__()
            for k, v in six.iteritems(self.__dict__):
                if k == '_result_cache':
                    obj.__dict__[k] = None
                else:
                    obj.__dict__[k] = deepcopy(v, memo)

            return obj

        def __getitem__(self, k):
            expected_types = (slice, ) + six.integer_types
            if not isinstance(k, expected_types):
                raise UnexpectedTypeError(expected_types, k)
            else:
                self._fetch_all()
                return self._result_cache[k]

        def __iter__(self):
            self._fetch_all()
            return iter(self._result_cache)

        def __len__(self):
            self._fetch_all()
            return len(self._result_cache)

        def __or__(self, other):
            if isinstance(other, TreeQuerySet):
                return TreeQuerySet(self._nodes_queryset | other._nodes_queryset)
            else:
                return TreeQuerySet(self._nodes_queryset | other)

        def __repr__(self):
            data = list(self[:REPR_OUTPUT_SIZE + 1])
            if len(data) > REPR_OUTPUT_SIZE:
                data[-1] = "...(remaining elements truncated)..."

            return repr(data)

        # PRIVATE METHODS

        def _clone(self, *args, **kwargs):
            return TreeQuerySet(self._nodes_queryset._clone(*args, **kwargs))

        def _fetch_all(self):
            if self._result_cache is None:
                self._result_cache = self._fetch_trees()

        def _fetch_trees(self, prefetch_related_objects=True):
            qs = self._nodes_queryset
            opts = qs.model._mptt_meta

            # Force depth-first order.
            qs = qs.order_by(opts.tree_id_attr, opts.left_attr)

            # Avoid unnecessary iterations.
            if (qs._result_cache
                    or (prefetch_related_objects
                            and qs._prefetch_related_lookups)):
                qs._fetch_all()
                nodes = qs._result_cache
            else:
                nodes = list(qs.iterator())

            top_nodes = []
            if nodes:
                current_path = []
                parent_attr = opts.parent_attr
                root_level = None
                for node in nodes:
                    # Get the current mptt node level.
                    node_level = node.get_level()

                    if root_level is None:
                        # First iteration, so set the root level to the top node
                        # level.
                        root_level = node_level

                    if node_level < root_level:
                        # Nodes were provided in an order other than depth-first.
                        msg = '{0} not in depth-first order'
                        raise ValueError(msg.format(self.__class__.__name__))

                    # Set up the attribute on the node that will store cached
                    # children, which is used by Nestable.get_children().
                    node._children = []

                    # Do the same for the attribute that will store cached
                    # descendants, which is used by Nestable.get_descendant().
                    node._descendants = []

                    # And set True the attribute that controls if the  subtrees
                    # are loaded, which is used by Nestable.get_subtrees().
                    node._subtrees = True

                    # Remove nodes not in the current branch.
                    while len(current_path) > node_level - root_level:
                        current_path.pop(-1)

                    if node_level == root_level:
                        # Add the root to the list of top nodes, which will be
                        # returned.
                        top_nodes.append(node)
                    else:
                        # Cache the parent on the current node, and attach the
                        # current node to the parent's list of children.
                        node_parent = current_path[-1]
                        setattr(node, parent_attr, node_parent)
                        node_parent._children.append(node)

                        # Attach the current node to the list of descendants of
                        # each ancestor.
                        for node_ancestor in current_path:
                            node_ancestor._descendants.append(node)


                    # Add the current node to end of the current path.
                    #
                    # The last node in the current path is the parent for the
                    # next iteration, unless the next iteration is higher up
                    # the tree (a new branch), in which case the paths below it
                    # (e.g., this one) will be removed from the current path
                    # during the next iteration.
                    #
                    current_path.append(node)

            return top_nodes

        # PUBLIC METHODS

        def all(self):
            return TreeQuerySet(self._nodes_queryset.all(*args, **kwargs))

        def annotate(self, *args, **kwargs):
            return TreeQuerySet(self._nodes_queryset.annotate(*args, **kwargs))

        def count(self):
            self._fetch_all()
            return len(self._result_cache)

        def defer(self, *fields):
            return TreeQuerySet(self._nodes_queryset.defer(*fields))

        def distinct(self, *field_names):
            return TreeQuerySet(self._nodes_queryset.distinct(*field_names))

        def exclude(self, *args, **kwargs):
            return TreeQuerySet(self._nodes_queryset.exclude(*args, **kwargs))

        def filter(self, *args, **kwargs):
            return TreeQuerySet(self._nodes_queryset.filter(*args, **kwargs))

        def first(self):
            self._fetch_all()
            if self._result_cache:
                return self._result_cache[0]
            else:
                return None

        def iterator(self):
            return iter(self._fetch_trees(prefetch_related_objects=False))

        def last(self):
            self._fetch_all()
            if self._result_cache:
                return self._result_cache[-1]
            else:
                return None

        def only(self, *fields):
            return TreeQuerySet(self._nodes_queryset.only(*fields))

        def prefetch_related(self, *lookups):
            return TreeQuerySet(self._nodes_queryset.prefetch_related(*lookups))

        def select_related(self, *fields):
            return TreeQuerySet(self._nodes_queryset.select_related(*fields))

        def using(self, alias):
            return TreeQuerySet(self._nodes_queryset.using(alias))

        # PROPERTIES

        @property
        def db(self):
            return self._nodes_queryset.db

        @property
        def model(self):
            return self._nodes_queryset.model

        @property
        def ordered(self):
            return True

        @property
        def query(self):
            return self._nodes_queryset.query


    class NestableQuerySet(MPTTQuerySet):

        def trees(self):
            return TreeQuerySet(self)


    class NestableManager(MPTTManager):

        def get_queryset(self):
            return NestableQuerySet(self.model, using=self._db)

        def trees(self, *args, **kwargs):
            return self.get_queryset().trees(*args, **kwargs)

