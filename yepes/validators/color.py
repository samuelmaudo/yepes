# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from yepes.validators.base import Validator

COLOR_RE = re.compile('\A#(?:[0-F]{3}){1,2}\Z', re.IGNORECASE)


class ColorValidator(Validator):
    """
    Checks if the value is a valid hexadecimal color.
    """
    message = _('Enter a valid color.')

    def validate(self, value):
        return (COLOR_RE.search(force_text(value)) is not None)

