# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import traceback

from django.utils import six
from django.utils.encoding import force_text


def _is_relevant_tb_level(tb):
    return ('__unittest' in tb.tb_frame.f_globals)


def format_class_name(cls, encoding='utf-8'):
    """
    Returns the full name of the given class.
    """
    full_name = '.'.join((cls.__module__, cls.__name__))
    return force_text(full_name, encoding, errors='replace')


def format_exception_message(exc_info, encoding='utf-8'):
    """
    Returns the exception's message.
    """
    exc_class, exc_value, tb = exc_info
    if exc_value is None:
        # str exception
        msg = exc_class
    else:
        msg = exc_value

    return force_text(msg, encoding, errors='replace')


def format_exception_name(exc_info, encoding='utf-8'):
    """
    Returns the exception's name.
    """
    exc_class, ev, tb = exc_info
    name = exc_class.__name__
    return force_text(name, encoding, errors='replace')


def format_traceback(exc_info, encoding='utf-8'):
    """
    Returns the exception's traceback in a nice format.
    """
    ec, ev, tb = exc_info

    # Skip test runner traceback levels
    while tb and _is_relevant_tb_level(tb):
        tb = tb.tb_next

    # Our exception object may have been turned into a string, and Python
    # 3's traceback.format_exception() doesn't take kindly to that (it
    # expects an actual exception object). So we work around it, by doing
    # the work ourselves if ev is not an exception object.
    if isinstance(ev, BaseException):
        return ''.join(
            force_text(line, encoding, errors='replace')
            for line
            in traceback.format_exception(ec, ev, tb)
        )
    else:
        tb_data = ''.join(
            force_text(line, encoding, errors='replace')
            for line
            in traceback.format_tb(tb)
        )
        if not isinstance(ev, six.text_format):
            ev = force_text(repr(ev))

        return tb_data + ev

