# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from yepes.validators.base import Validator

DOMAIN_RE = re.compile(r"""^
    (?:[a-z0-9]+(?:-[a-z0-9]+)*\.)+
    (?:[a-z]{2,6})
$""", re.VERBOSE | re.IGNORECASE)

USER_RE = re.compile(r"""^
    [a-z0-9]+
    (?:[-_.+~'][a-z0-9]+)*
$""", re.VERBOSE | re.IGNORECASE)


class RestrictedEmailValidator(Validator):
    """
    A more restricted version of ``django.core.validators.EmailValidator``:

    At the user part, accepts only ASCII letters and numbers, dashes,
    underscores, dots and plus signs. Whereas, at the domain part, does not
    accept IP addresses or IDN domains.

    """
    message = _('Enter a valid email address.')

    def validate(self, value):
        address = force_text(value)
        if '@' not in address:
            return False

        user_part, domain_part = address.rsplit('@', 1)
        return (self.validate_domain(domain_part)
                and self.validate_user(user_part))

    def validate_domain(self, value):
        """
        Does not accept IP addresses or IDN domains.
        """
        return (DOMAIN_RE.search(value) is not None)


    def validate_user(self, value):
        """
        Accepts only ASCII letters, dashes, underscores and plus signs.
        """
        return (USER_RE.search(value) is not None)

