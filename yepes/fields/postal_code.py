# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes.fields.name import NameField
from yepes.validators import PostalCodeValidator


class PostalCodeField(NameField):

    description = _('Generic postal code')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 15)
        kwargs.setdefault('validators', [PostalCodeValidator()])
        super(PostalCodeField, self).__init__(*args, **kwargs)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        return ('yepes.fields.PostalCodeField', args, kwargs)

