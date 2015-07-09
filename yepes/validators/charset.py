# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from yepes.validators.base import LimitedValidator


class CharSetValidator(LimitedValidator):
    """
    Checks if the value consists solely on characters from the given ``charset``.

    Characters can be listed individually, but range of characters can be
    indicated by using a dash. For example, `'a-f'` is equivalent to `'abcdef'`.

    To add a dash to the charset, you can escape it with a backslash (e.g.
    `'a\-z'`) or place it at the beginning or at the end (e.g. `'a-'`).

    """
    message = _('Ensure this value contains only valid characters ({limit_value}).')

    def __init__(self, charset, message=None):
        self.limit_value = force_text(charset)
        self.regex = re.compile('\A[{0}]*\Z'.format(
            re.escape(self.limit_value).replace('\\-', '-')
        ))
        super(LimitedValidator, self).__init__(message)

    def validate(self, value):
        return (self.regex.search(force_text(value)) is not None)

