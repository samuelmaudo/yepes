# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _

DOMAIN_RE = re.compile(r"""^
    (?:[a-z0-9]+(?:-[a-z0-9]+)?\.)+
    (?:[a-z]{2,6})
$""", re.VERBOSE | re.IGNORECASE)

USER_RE = re.compile(r"""^
    [a-z0-9]+
    (?:[-.+_~][a-z0-9]+)*
$""", re.VERBOSE | re.IGNORECASE)


def validate_email_address(value):
    """
    A more restricted version of ``django.core.validators.validate_email()``:

    At the user part, accepts only ASCII letters, dashes, underscores and plus
    signs.

    And, at the domain part, does not accept IP addresses or IDN domains.

    """
    address = force_text(value)
    if address.count('@') != 1:
        raise ValidationError(_('Enter a valid email address.'))

    user_part, domain_part = address.rsplit('@', 1)
    validate_email_domain(domain_part)
    validate_email_user(user_part)


def validate_email_domain(value):
    """
    Does not accept IP addresses or IDN domains.
    """
    if not DOMAIN_RE.search(value):
        raise ValidationError(_('Enter a valid email domain.'))


def validate_email_user(value):
    """
    Accepts only ASCII letters, dashes, underscores and plus signs.
    """
    if not USER_RE.search(value):
        raise ValidationError(_('Enter a valid email user.'))

