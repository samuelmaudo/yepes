# -*- coding:utf-8 -*-

from django.template.base import Library
from django.template.defaultfilters import stringfilter
from django.utils.six.moves import xrange

from yepes.utils import htmlentities, unidecode

register = Library()


@register.filter(is_safe=True)
@stringfilter
def endswith(value, arg):
    return value.endswith(arg)


@register.filter(is_safe=False)
def get(value, arg):
    try:
        return getattr(value, arg)
    except AttributeError:
        try:
            return value[arg]
        except (AttributeError, KeyError):
            return ''


@register.filter(is_safe=False)
def pk(value):
    return getattr(value, 'pk', None)


@register.filter(is_safe=False)
def roundlist(iterable, i):
    L = list(iterable)
    try:
        i = int(i)
    except:
        pass
    else:
        if L:
            lg = len(L)
            excess = ((float(lg) / i) - (int(lg) / i)) * i
            remaining = int(i - int(round(excess) or i))
        else:
            remaining = i
        L.extend(None for i in xrange(remaining))
    return L


@register.filter(is_safe=True)
@stringfilter
def startswith(value, arg):
    return value.startswith(arg)


@register.filter(is_safe=True)
@stringfilter
def strip(value, arg=None):
    return value.strip(arg)


@register.filter(is_safe=True)
def toascii(value):
    return unidecode(htmlentities.decode(value))


@register.filter(is_safe=True)
def toentities(value):
    return htmlentities.encode(value)


@register.filter(is_safe=True)
def tounicode(value):
    return htmlentities.decode(value)

