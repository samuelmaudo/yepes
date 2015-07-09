# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from yepes.validators.base import Validator

KEY_RE = re.compile('\A[A-Z_][A-Z0-9_]*\Z', re.IGNORECASE)


class IdentifierValidator(Validator):
    """
    Checks if the value is a valid identifier.
    """
    message = _('Enter a valid identifier.')

    def validate(self, value):
        return (KEY_RE.search(force_text(value)) is not None)

