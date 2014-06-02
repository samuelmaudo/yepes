# -*- coding:utf-8 -*-

from __future__ import unicode_literals


class LookupTypeError(TypeError):

    def __init__(self, lookup_type):
        msg = "Lookup type '{0}' not supported"
        super(LookupTypeError, self).__init__(msg.format(lookup_type))
        self.lookup_type = lookup_type


class MissingAttributeError(AttributeError):

    def __init__(self, obj, attr_name):
        args = (
            obj.__class__.__name__,
            attr_name,
        )
        msg = "'{0}' object has no attribute '{1}'"
        super(MissingAttributeError, self).__init__(msg.format(*args))
        self.obj = obj
        self.attr_name = attr_name


class ReadOnlyAttributeError(AttributeError):

    def __init__(self, obj, attr_name):
        args = (
            obj.__class__.__name__,
            attr_name,
        )
        msg = "'{0}.{1}' attribute cannot be assigned"
        super(ReadOnlyAttributeError, self).__init__(msg.format(*args))
        self.obj = obj
        self.attr_name = attr_name


class ReadOnlyObjectError(AttributeError):

    def __init__(self, obj, attr_name):
        args = (
            obj.__class__.__name__,
            attr_name,
        )
        msg = "'{0}' does not accept attribute assignment"
        super(ReadOnlyObjectError, self).__init__(msg.format(*args))
        self.obj = obj


class UnexpectedTypeError(TypeError):

    def __init__(self, expected_type, received_type):
        if not isinstance(expected_type, (tuple, list)):
            expected_type = (expected_type, )
        args = (
            ' or '.join(cls.__name__ for cls in expected_type),
            received_type.__class__.__name__,
        )
        msg = '{0} was expected, got {1}'
        super(UnexpectedTypeError, self).__init__(msg.format(*args))
        self.expected_type = expected_type
        self.received_type = received_type
