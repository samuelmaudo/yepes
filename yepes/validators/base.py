# -*- coding:utf-8 -*-

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class BaseValidator(object):
    code = 'invalid'
    message = _('Enter a valid value.')

    def __init__(self, message=None):
        if message is not None:
            self.message = message

    def invalid(self, value):
        params = {'value': value}
        raise ValidationError(
            self.message.format(**params),
            code=self.code,
            params=params)

