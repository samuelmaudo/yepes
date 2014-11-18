# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.encoding import force_text


def normalize_email(address):
    """
    The local part of an e-mail address is case-sensitive, the domain part is
    not. This function lowercases the host and should be used in all email
    handling.
    """
    address = force_text(address or '').strip()
    if address.isupper():
        # If user typed the entire address in uppercase letters,
        # surely it does not contain any.
        return address.lower()
    try:
        local_part, domain_part = address.rsplit('@', 1)
    except ValueError:
        return address
    else:
        return '@'.join((local_part, domain_part.lower()))

