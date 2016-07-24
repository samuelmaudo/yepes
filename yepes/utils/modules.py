# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import sys
import traceback
import warnings


class MissingModuleError(ImportError):

    def __init__(self, module_path):
        msg = "Module '{0}' could not be imported."
        super(MissingModuleError, self).__init__(msg.format(module_path))


def import_module(module_path, ignore_missing=False, ignore_internal_errors=False):
    """
    Returns the module located at ``module_path``. If module had not been
    previously imported, tries to import it and add it to ``sys.modules``.

    This is similar to ``importlib.import_module()`` but this function allows
    to ignore certain import errors.

    Args:

        module_path (str): Name of the module to be retrieved.

        ignore_missing (bool): Whether ignore import errors when module is not
                found at the specified path. Defaults to False.

        ignore_internal_errors (bool): Whether ignore import errors when one of
                the module dependencies cannot be imported. Also ignores syntax
                errors and issues a warning when an error is ignored (this is
                for development purposes). Defaults to False.

    Returns:

        The requested module or None if an error occurs.

    Example:

        >>> import_module('yepes')
        <module 'yepes' from 'yepes/__init__.pyc'>

    Raises:

        MissingModuleError: If the requested module cannot be found and
                ``ignore_missing`` is False.

        ImportError: If a module dependency cannot be imported and
                ``ignore_internal_errors`` is False.

        SyntaxError: If module code has a syntax error and
                ``ignore_internal_errors`` is False.

    """
    try:
        __import__(module_path)
    except ImportError as e:
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
        if len(stack_trace_entries) <= 1:
            if ignore_missing:
                return None
            else:
                raise MissingModuleError(module_path)
        else:
            if ignore_internal_errors:
                warnings.warn(str(e), ImportWarning, 2)
                return None
            else:
                raise e
    except SyntaxError as e:
        if ignore_internal_errors:
            warnings.warn(str(e), SyntaxWarning, 2)
            return None
        else:
            raise e

    return sys.modules[module_path]

