# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.forms.fields.char import CharField
from yepes.validators import IdentifierValidator


class IdentifierField(CharField):

    default_validators = [IdentifierValidator()]

    def __init__(self, *args, **kwargs):
        kwargs['normalize_spaces'] = False
        kwargs['trim_spaces'] = True
        super(IdentifierField, self).__init__(*args, **kwargs)

