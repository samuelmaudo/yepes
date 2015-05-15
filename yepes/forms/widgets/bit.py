# -*- coding:utf-8 -*-

import operator

from django.forms import CheckboxSelectMultiple
from django.utils import six
from django.utils.six.moves import reduce

from yepes.types import Bit


class BitWidget(CheckboxSelectMultiple):

    def render(self, name, value, attrs=None, choices=()):
        value_set = set()
        if value and isinstance(value, (Bit, six.integer_types)):
            for key, verbose in self.choices:
                if value & key:
                    value_set.add(key)

        value = value_set
        return super(BitWidget, self).render(name, value, attrs)

    def _has_changed(self, initial, data):
        data = [int(d) for d in data]
        if not data:
            return (not initial)
        else:
            return (initial != reduce(operator.or_, data))

