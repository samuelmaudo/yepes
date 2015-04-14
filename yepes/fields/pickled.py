# -*- coding:utf-8 -*-

from base64 import b64decode, b64encode
from copy import deepcopy
try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.db import models
from django.db.models.fields.subclassing import Creator as SubfieldDescriptor
from django.utils import six
from django.utils.encoding import force_bytes

from yepes.exceptions import LookupTypeError
from yepes.utils.properties import cached_property


class PickledObjectField(models.BinaryField):
    """
    A field that accepts *any* python object and store it in the database.

    The pickling protocol must be explicitly specified (by default 2), rather
    than as -1 or ``HIGHEST_PROTOCOL``, because we don't want the protocol
    to change over time. If it did, ``exact`` and ``in`` lookups would likely
    fail, since pickle would now be generating a different string.

    """
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
        kwargs.setdefault('editable', False)
        super(PickledObjectField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        # Do not use ``models.SubfieldBase`` because when a model instance is
        # saved for the first time, ``subclassing.Creator`` is called even if
        # a subclass overrode the descriptor.
        # This raises a weird error in ``CalculatedMixin`` subclasses such as
        # the taxes field of ``Order`` instances.
        super(PickledObjectField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, SubfieldDescriptor(self))

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

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.BinaryField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

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

