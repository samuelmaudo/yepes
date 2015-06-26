# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.encoding import force_text

from yepes.validators.email import DOMAIN_RE, USER_RE


def normalize_email(address):
    """
    Returns a copy of the address with the domain part in lowercase. If the
    entire address was in uppercase letters, the user part will also be lowered.

    The reason is that the local part of an e-mail address is case-sensitive,
    but the domain part is not. However, if user typed the entire address in
    uppercase letters, surely it does not contain any.

    NOTE: This function should be used in all email handling.

    """
    address = force_text(address or '').strip()
    if '@' not in address:
        return address
    elif address.isupper():
        return address.lower()
    else:
        local_part, domain_part = address.rsplit('@', 1)
        return '@'.join((local_part, domain_part.lower()))


def validate_email(address):
    """
    Returns True or False depending on whether the given ``address`` is a valid
    email address or not.

    Applies the same restrictions as ``yepes.validators.RestrictedEmailValidator``.

    """
    address = force_text(address)
    if '@' not in address:
        return False

    user_part, domain_part = address.rsplit('@', 1)
    return (DOMAIN_RE.search(domain_part) is not None
            and USER_RE.search(user_part) is not None)

