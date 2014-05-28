# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.db import models
from django.core import validators
from django.utils.translation import ugettext as _


class KeyField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('max_length', 31)
        kwargs.setdefault('unique', True)
        super(KeyField, self).__init__(*args, **kwargs)
        self.validators = [
            validators.RegexValidator(
                re.compile('^[_a-zA-Z0-9]{{1,{0}}}$'.format(
                                        self.max_length - 1)),
                _('Enter a valid key.'))
        ]

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.CharField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

