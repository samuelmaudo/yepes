# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.template.base import Library
from django.template.defaultfilters import stringfilter
from django.utils.six.moves import range

from yepes.utils import htmlentities, unidecode

register = Library()


@register.filter(is_safe=True)
@stringfilter
def endswith(value, arg):
    return value.endswith(arg)


@register.filter(is_safe=False)
def first(value):
    try:
        return next(iter(value))
    except (KeyError, StopIteration, TypeError):
        return None


@register.filter(is_safe=False)
def get(value, arg):
    try:
        return getattr(value, arg)
    except (AttributeError, TypeError):
        try:
            return value[arg]
        except (AttributeError, KeyError, IndexError, TypeError):
            return None


@register.filter(is_safe=False)
def last(value):
    try:
        iterator = iter(value)
    except TypeError:
        return None
    else:
        item = None
        try:
            for item in iterator:
                pass
        except KeyError:
            return None
        else:
            return item


@register.filter(is_safe=False)
def pk(value):
    try:
        return value._get_pk_val()
    except AttributeError:
        return None


@register.filter(is_safe=False)
def roundlist(value, arg):
    sequence = list(value)
    try:
        nelements = int(arg)
    except (ValueError, TypeError):
        pass
    else:
        if not sequence:
            remaining = nelements
        else:
            excess = len(sequence) % nelements
            if not excess:
                remaining = 0
            else:
                remaining = nelements - excess

        sequence.extend(None for i in range(remaining))

    return sequence


@register.filter(is_safe=True)
@stringfilter
def startswith(value, arg):
    return value.startswith(arg)


@register.filter(is_safe=True)
@stringfilter
def strip(value, arg=None):
    return value.strip(arg)


@register.filter(is_safe=False)
@stringfilter
def toascii(value):
    return unidecode(htmlentities.decode(value))


@register.filter(is_safe=True)
@stringfilter
def toentities(value):
    return htmlentities.encode(value)


@register.filter(is_safe=False)
@stringfilter
def tounicode(value):
    return htmlentities.decode(value)

