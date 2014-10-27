# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals

from django.db.models import F, Q


class Operation(object):

    needs_value = True

    def __init__(self, field, value=None):
        self.field_name = field.name
        self.value = value

    def __repr__(self):
        args = (
            self.__class__.__name__,
            self.field_name,
            self.value,
        )
        return '<{0} {1}, {2}>'.format(*args)

    def describe(self):
        args = (
            self.label.capitalize(),
            self.field_name,
            self.value,
        )
        return '{0} {1}, {2}'.format(*args)

    def as_expression(self):
        raise NotImplementedError('subclasses of Operation must provide an as_expression() method')

    def run(self, obj):
        raise NotImplementedError('subclasses of Operation must provide a run() method')


# ASSIGNMENT OPERATIONS ########################################################


class Set(Operation):

    label = 'set'

    def as_expression(self):
        return self.value

    def describe(self):
        return 'Set {0} value to {1}'.format(self.field_name, self.value)

    def run(self, obj):
        setattr(obj, self.field_name, self.value)


class SetNull(Set):

    label = 'set_null'
    needs_value = False


# MATHEMATICAL OPERATIONS ######################################################


class Add(Operation):

    label = 'add'

    def as_expression(self):
        return (F(self.field_name) + self.value)

    def describe(self):
        return 'Add {1} to {0} value'.format(self.field_name, self.value)

    def run(self, obj):
        old_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, old_value + self.value)


class Sub(Operation):

    label = 'sub'

    def as_expression(self):
        return (F(self.field_name) - self.value)

    def describe(self):
        return 'Subtract {1} from {0} value'.format(self.field_name, self.value)

    def run(self, obj):
        old_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, old_value - self.value)


class Mul(Operation):

    label = 'mul'

    def as_expression(self):
        return (F(self.field_name) * self.value)

    def describe(self):
        return 'Multiply {0} value by {1}'.format(self.field_name, self.value)

    def run(self, obj):
        old_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, old_value * self.value)


class Div(Operation):

    label = 'div'

    def as_expression(self):
        return (F(self.field_name) / self.value)

    def describe(self):
        return 'Divide {0} value between {1}'.format(self.field_name, self.value)

    def run(self, obj):
        old_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, old_value / self.value)


# LOGICAL OPERATIONS ###########################################################


class Swap(Operation):

    label = 'swap'
    needs_value = False

    def describe(self):
        return 'Swap {0} value'.format(self.field_name)

    def run(self, obj):
        old_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, not old_value if old_value is not None else None)


# STRING OPERATIONS ############################################################


class Lower(Operation):

    label = 'lower'
    needs_value = False

    def describe(self):
        return 'Convert cased characters of {0} value to lowercase'.format(self.field_name)

    def run(self, obj):
        old_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, old_value.lower())


class Upper(Operation):

    label = 'upper'
    needs_value = False

    def describe(self):
        return 'Convert cased characters of {0} value to uppercase'.format(self.field_name)

    def run(self, obj):
        old_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, old_value.upper())


class Capitalize(Operation):

    label = 'capitalize'
    needs_value = False

    def describe(self):
        return 'Capitalize the first character of {0} value'.format(self.field_name)

    def run(self, obj):
        old_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, old_value.capitalize())


class Title(Operation):

    label = 'title'
    needs_value = False

    def describe(self):
        return 'Capitalize the first character of each word of {0} value'.format(self.field_name)

    def run(self, obj):
        old_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, old_value.title())


class SwapCase(Operation):

    label = 'swap_case'
    needs_value = False

    def describe(self):
        return 'Convert uppercase characters of {0} value to lowercase and vice versa'.format(self.field_name)

    def run(self, obj):
        old_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, old_value.swapcase())


class Strip(Operation):

    label = 'strip'
    needs_value = False

    def describe(self):
        return 'Remove leading and trailing whitespaces of {0} value'.format(self.field_name)

    def run(self, obj):
        old_value = getattr(obj, self.field_name)
        setattr(obj, self.field_name, old_value.strip())

