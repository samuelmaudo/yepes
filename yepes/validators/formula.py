# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes.types import Formula
from yepes.validators.base import LimitedValidator


class FormulaValidator(LimitedValidator):
    """
    Checks if the value is a well-written formula.
    """
    message = _('Correct the syntax of this formula.')

    def __init__(self, variables=None, message=None):
        limit_value = list(variables) if variables else []
        super(FormulaValidator, self).__init__(limit_value, message)

    def validate(self, value):
        return Formula(value).validate(*self.limit_value)

