# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.forms.fields.char import CharField
from yepes.validators import FormulaValidator


class FormulaField(CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('normalize_spaces', False)
        kwargs.setdefault('trim_spaces', True)
        self.variables = list(kwargs.pop('variables', []))
        super(FormulaField, self).__init__(*args, **kwargs)
        self.validators.append(FormulaValidator(self.variables))

