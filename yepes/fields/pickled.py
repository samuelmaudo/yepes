# -*- coding:utf-8 -*-

from base64 import b64decode, b64encode
from copy import deepcopy

from django.db import models
from django.utils import six
from django.utils.encoding import force_bytes
from django.utils.six.moves import cPickle as pickle
from django.utils.translation import ugettext_lazy as _

from yepes.exceptions import LookupTypeError
from yepes.fields.calculated import CalculatedField
from yepes.utils.deconstruct import clean_keywords
from yepes.utils.properties import cached_property


class PickledObjectField(CalculatedField, models.BinaryField):
    """
    A field that accepts *any* python object and store it in the database.

    The pickling protocol must be explicitly specified (by default 2), rather
    than as -1 or ``HIGHEST_PROTOCOL``, because we don't want the protocol
    to change over time. If it did, ``exact`` and ``in`` lookups would likely
    fail, since pickle would now be generating a different string.

    """
    description = _('Pickled object')

    _prefix = '{[(#'
    _suffix = '#)]}'

    @cached_property
    def _prefix_len(self):
        return len(self._prefix)

    @cached_property
    def _suffix_len(self):
        return len(self._suffix)

    def __init__(self, *args, **kwargs):
        self.protocol = kwargs.pop('protocol', 2)
        super(PickledObjectField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(PickledObjectField, self).deconstruct()
        path = path.replace('yepes.fields.pickled', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'protocol': 2,
        })
        return name, path, args, kwargs

    def dump(self, obj):
        """
        Return the pickled representation of the object as a bytes object.

        We use ``deepcopy()`` here to avoid a problem with cPickle, where
        ``dumps()`` can generate different character streams for same lookup
        value if they  are referenced differently.

        The reason this is important is because we do all of our lookups as
        simple string matches, thus the character streams must be the same for
        the lookups to work properly.

        """
        return pickle.dumps(deepcopy(obj), self.protocol)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        else:
            return self.load(value)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise LookupTypeError(lookup_type)

    def get_prep_value(self, value):
        if value is not None:
            return self.dump(value)
        else:
            return value

    def load(self, bytes):
        """
        Read a pickled object hierarchy from a bytes object and return the
        reconstituted object hierarchy specified therein.
        """
        if bytes:
            return pickle.loads(force_bytes(bytes))
        else:
            return None

    def to_python(self, value):
        if isinstance(value, six.binary_type):
            return self.load(value)
        elif isinstance(value, buffer if six.PY2 else memoryview):
            return self.load(six.binary_type(value))
        elif (isinstance(value, six.text_type)
                and value.startswith(self._prefix)
                and value.endswith(self._suffix)):
            return self.value_from_string(value)
        else:
            return value

    def value_from_string(self, string):
        dumped_value = string[self._prefix_len:-self._suffix_len]
        return self.load(b64decode(dumped_value.encode('ascii')))

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        dumped_value = b64encode(self.dump(value)).decode('ascii')
        return ''.join(self._prefix, dumped_value, self._suffix)

