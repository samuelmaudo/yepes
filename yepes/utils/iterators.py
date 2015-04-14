# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals

from itertools import islice


def isplit(iterable, size):
    """
    Makes an iterator that returns batches of the indicated ``size`` of
    elements from the ``iterable``::

        >>> list(isplit([1, 2, 3, 4, 5, 6, 7], 3))
        [[1, 2, 3], [4, 5, 6], [7]]

    If the length of the ``iterable`` is not evenly divisible by ``size``, the
    last returned batch will be shorter.

    This is useful for working with large datasets, avoiding load the entire
    dataset in RAM.

    """
    if size < 1:
        msg = '``size`` argument must be an integer greater than zero.'
        raise ValueError(msg)

    it = iter(iterable)
    batch = list(islice(it, size))
    while batch:
        yield batch
        batch = list(islice(it, size))


def split(iterable, size):
    """
    Returns a list with batches of the indicated ``size`` of elements from the
    ``iterable``::

        >>> split([1, 2, 3, 4, 5, 6, 7], 3)
        [[1, 2, 3], [4, 5, 6], [7]]

    If the length of the ``iterable`` is not evenly divisible by ``size``, the
    last returned batch will be shorter.

    """
    return list(isplit(iterable, size))

