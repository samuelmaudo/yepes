# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.forms.fields.char import CharField
from yepes.validators import PostalCodeValidator


class PostalCodeField(CharField):

    default_validators = [PostalCodeValidator()]

    def __init__(self, *args, **kwargs):
        kwargs['force_lower'] = False
        kwargs['force_upper'] = True
        kwargs['normalize_spaces'] = True
        kwargs['trim_spaces'] = False
        super(PostalCodeField, self).__init__(*args, **kwargs)

