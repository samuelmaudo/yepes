# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import sys

from django.utils import six


def raise_chained_exception(new_exc_class):
    exc_class, exc, tb = sys.exc_info()
    new_exc = new_exc_class(six.text_type(exc))
    if six.PY2:
        raise new_exc_class, new_exc, tb
    else:
        raise new_exc.with_traceback(tb)

