# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import random

from django.utils.six.moves import range
from django.utils.translation import ugettext_lazy as _

from yepes.fields.char import CharField
from yepes.utils.deconstruct import clean_keywords


class GuidField(CharField):

    default_length = 12
    default_charset = '0123456789abcdef'
    description = _('Global Unique Identifier')

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = False
        kwargs.setdefault('charset', self.default_charset)
        kwargs.setdefault('db_index', True)
        kwargs['force_ascii'] = False
        kwargs['force_lower'] = False
        kwargs['force_upper'] = False
        kwargs.setdefault('max_length', self.default_length)
        kwargs['normalize_spaces'] = False
        kwargs['null'] = False
        kwargs['trim_spaces'] = True
        super(GuidField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(GuidField, self).deconstruct()
        path = path.replace('yepes.fields.guid', 'yepes.fields')
        clean_keywords(self, kwargs, defaults={
            'charset': self.default_charset,
            'db_index': True,
            'max_length': self.default_length,
        }, immutables=[
            'blank',
            'force_ascii',
            'force_lower',
            'force_upper',
            'normalize_spaces',
            'null',
            'trim_spaces',
        ])
        return name, path, args, kwargs

    def generate_guid(self):
        return ''.join(random.choice(self.charset)
                       for i in range(self.max_length))

    def get_default(self):
        guid = self.generate_guid()

        if self.unique:
            lookup = self.get_validator_unique_lookup_type()
            qs = self.model._default_manager.get_queryset()
            for i in range(63):
                if qs.filter(**{lookup: guid}).exists():
                    guid = self.generate_guid()
                else:
                    break

        return guid

