# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import random
import re

from django.core import validators
from django.db import models
from django.utils.six.moves import xrange
from django.utils.translation import ugettext as _

TOKEN_RE = '^[{0}]{{{1},{1}}}$'


class GuidField(models.CharField):

    default_length = 12
    default_charset = '0123456789abcdef'
    description = _('Global Unique Identifier')

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = False
        self.charset = kwargs.pop('charset', self.default_charset)
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('max_length', self.default_length)
        kwargs['null'] = False
        super(GuidField, self).__init__(*args, **kwargs)
        self.validators = [
            validators.RegexValidator(
                re.compile(TOKEN_RE.format(self.charset, self.max_length)),
                _('Enter a valid value.'))
        ]

    def generate_guid(self):
        return ''.join(random.choice(self.charset)
                       for i in xrange(self.max_length))

    def get_default(self):
        guid = super(GuidField, self).get_default()
        if not guid:
            guid = self.generate_guid()

        if self.unique:
            lookup = self.get_validator_unique_lookup_type()
            qs = self.model._default_manager.get_queryset()
            for i in xrange(63):
                if qs.filter(**{lookup: guid}).exists():
                    guid = self.generate_guid()
                else:
                    break

        return guid

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.CharField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

