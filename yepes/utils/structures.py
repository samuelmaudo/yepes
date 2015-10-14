# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals

from collections import OrderedDict

from django.utils import six


class OrderedDictThatIteratesOverValues(OrderedDict):

    def __iter__(self):
        return six.itervalues(self)

    def copy(self):
        other = self.__class__()
        for key in six.iterkeys(self):
            other[key] = self[key]
        return other

    if six.PY2:

        def items(self):
            return list(self.iteritems())

        def iteritems(self):
            for k in self.iterkeys():
                yield (k, self[k])

        def iterkeys(self):
            return super(OrderedDictThatIteratesOverValues, self).__iter__()

        def itervalues(self):
            for k in self.iterkeys():
                yield self[k]

        def keys(self):
            return list(self.iterkeys())

        def values(self):
            return list(self.itervalues())

    else:

        def items(self):
            for k in self.keys():
                yield (k, self[k])

        def keys(self):
            return super(OrderedDictThatIteratesOverValues, self).__iter__()

        def values(self):
            for k in self.keys():
                yield self[k]

