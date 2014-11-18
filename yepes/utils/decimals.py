# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import decimal

__all__ = ('force_decimal', 'round_decimal', 'sum_decimals')

ZERO = decimal.Decimal('0')


def force_decimal(value='0'):
    if isinstance(value, decimal.Decimal):
        return value
    try:
        return value.to_decimal()
    except AttributeError:
        return decimal.Decimal(value)


def round_decimal(value, precision=None, exponent=None):
    if exponent is None:
        if precision is None:
            raise AttributeError
        else:
            exponent = decimal.Decimal('0.' + '0' * precision)

    return force_decimal(value).quantize(exponent)


def sum_decimals(decimals):
    """
    Sums the given ``decimals`` and returns the total.
    """
    return sum(decimals, ZERO)

