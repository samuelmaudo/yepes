# -*- coding:utf-8 -*-

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class Validator(object):
    """
    Base class for validator implementations.

    Subclasses must provide ``validate()`` method.

    """
    code = 'invalid'
    message = _('Enter a valid value.')

    def __init__(self, message=None):
        if message is not None:
            self.message = message

    def __call__(self, value):
        if not self.validate(value):
            msg = self.get_message(value)
            raise ValidationError(msg, code=self.code)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.message == other.message
            and self.code == other.code
        )

    def deconstruct(self):
        """
        Returns a 3-tuple of class import path, positional arguments, and
        keyword arguments.
        """
        cls = self.__class__
        module = cls.__module__
        if module.startswith('yepes.validators'):
            module = 'yepes.validators'

        path = '.'.join((module, cls.__name__))
        args = []
        kwargs = {}
        if self.message != cls.message:
            kwargs['message'] = self.message

        return (path, args, kwargs)

    def get_message(self, value):
        """Returns a formatted error message."""
        params = self.get_message_params(value)
        return self.message.format(**params)

    def get_message_params(self, value):
        """Returns a dict with the message parameters."""
        return {'value': value}

    def validate(self, value):
        """
        Checks ``value`` and returns True or False depending on whether it is
        valid or not.
        """
        raise NotImplementedError('Subclasses of Validator must provide a validate() method')


class LimitedValidator(Validator):
    """
    Base class for implement validators that use a ``limit_value`` to validate
    the given values.

    Subclasses must provide ``validate()`` method.

    """
    def __init__(self, limit_value, message=None):
        self.limit_value = limit_value
        super(LimitedValidator, self).__init__(message)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.limit_value == other.limit_value
            and self.message == other.message
            and self.code == other.code
        )

    def deconstruct(self):
        """
        Returns a 3-tuple of class import path, positional arguments, and
        keyword arguments.
        """
        path, args, kwargs = super(LimitedValidator, self).deconstruct()
        kwargs['limit_value'] = self.limit_value
        return (path, args, kwargs)

    def get_message_params(self, value):
        """Returns a dict with the message parameters."""
        params = super(LimitedValidator, self).get_message_params(value)
        params['limit_value'] = self.limit_value
        return params

