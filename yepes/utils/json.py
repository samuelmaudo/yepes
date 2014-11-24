# -*- coding:utf-8 -*-

from __future__ import absolute_import, unicode_literals

import datetime
import decimal

from json import (
    dump as default_dump,
    dumps as default_dumps,
    load,
    loads,
    JSONDecoder,
    JSONEncoder as DefaultJSONEncoder,
)

__all__ = ('dump', 'dumps', 'load', 'loads', 'JSONDecoder', 'JSONEncoder')


class JSONEncoder(DefaultJSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            r = o.isoformat()
            if o.microsecond:
                r = r[:12] + r[15:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, decimal.Decimal):
            return self.default_decimal(o)
        try:
            o = o.to_decimal()
        except AttributeError:
            return super(JSONEncoder, self).default(o)
        else:
            return self.default_decimal(o)

    def default_decimal(self, o):
        o = str(o)
        if '.' not in o:
            return int(o)

        i, d = o.split('.', 1)
        d = d.rstrip('0')
        if not d:
            return int(i)
        else:
            return float(o)


def dump(*args, **kwargs):
    kwargs.setdefault('cls', JSONEncoder)
    return default_dump(*args, **kwargs)


def dumps(*args, **kwargs):
    kwargs.setdefault('cls', JSONEncoder)
    return default_dumps(*args, **kwargs)

