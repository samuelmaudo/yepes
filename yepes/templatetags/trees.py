# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from collections import Iterable

from django.db.models import Model
from django.db.models.query import QuerySet
from django.template import Library
from django.utils.safestring import mark_safe

from yepes.managers import TreeQuerySet
from yepes.template import DoubleTag

register = Library()


## {% recurse tree %} ##########################################################


class RecurseTag(DoubleTag):

    def _render_node(self, context, node):
        bits = (
            self._render_node(context, child)
            for child
            in node.get_children()
        )
        context.push()
        context['node'] = node
        context['children'] = mark_safe(''.join(bits))
        rendered = self.nodelist.render(context)
        context.pop()
        return rendered

    def process(self, tree):
        if isinstance(tree, Model):
            nodes = tree.get_subtrees()
        elif isinstance(tree, Iterable):
            nodes = tree
            if (isinstance(nodes, QuerySet)
                    and not isinstance(nodes, TreeQuerySet)):
                nodes = TreeQuerySet(nodes)
        else:
            return ''

        bits = (
            self._render_node(self.context, node)
            for node
            in nodes
        )
        return ''.join(bits)

register.tag('recurse', RecurseTag.as_tag())

