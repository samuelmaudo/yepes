# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import sys
import traceback


def get_module(name, ignore_missing=False, ignore_internal_errors=False):
    try:
        __import__(name)
    except ImportError:
        """
        There are two reasons why there is ``ImportError``:
        1. The module does not exist at the specified path.
        2. The path is right, but one of the module dependencies cannot be
           imported.

        ``ImportError`` does not provide easy way to distinguish those two
        cases. Fortunately, the traceback of the ``ImportError`` starts at
        ``__import__`` statement. If the traceback has more than one entry,
        it means the path was correct and that is a subsequent dependence
        that generated the error.

        """
        error_type, error_value, error_traceback = sys.exc_info()
        stack_trace_entries = traceback.extract_tb(error_traceback)
        if len(stack_trace_entries) > 1:
            if ignore_internal_errors:
                return None
            else:
                raise
        else:
            if ignore_missing:
                return None
            else:
                raise

    return sys.modules[name]

