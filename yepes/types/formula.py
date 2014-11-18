# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import operator
import re

from django.utils import six
from django.utils.encoding import force_str, force_text
from django.utils.encoding import python_2_unicode_compatible

from yepes.exceptions import MissingAttributeError
from yepes.types.undefined import Undefined
from yepes.utils.decimals import force_decimal

__all__ = ('Formula', )

DECIMAL_RE = re.compile(r'([0-9]|[0-9]+[.][0-9]*|[.][0-9]+)')
PARENTHESES_RE = re.compile(r'\(([^()]*)\)')
TOKENS_RE = re.compile(r'([-]|[+]|[._a-zA-Z0-9]+|[^ ]+)')
VARIABLE_RE = re.compile(r'[_a-zA-Z][_a-zA-Z0-9]*')


@python_2_unicode_compatible
class Formula(object):

    def __init__(self, formula):
        self.formula = force_text(formula).lower()
        self.variables = {}

    def __getattr__(self, name):
        if name in self.variables:
            return self.variables[name]
        else:
            raise MissingAttributeError(self, name)

    def __setattr__(self, name, value):
        if name.startswith('_') or name in ('formula', 'variables'):
            super(Formula, self).__setattr__(name, value)
        else:
            if isinstance(value, (six.integer_types, float)):
                value = force_decimal(value)
            self.variables[name] = value

    def __repr__(self):
        args = (
            self.__class__.__name__,
            self.formula,
        )
        return force_str('<{0}: {1}>'.format(*args))

    def __str__(self):
        return self.formula

    def __boolean__(self):
        return (len(self.formula) > 0)

    def __nonzero__(self):
        return self.__bool__()

    def calculate(self, **variables):
        form = self.formula
        vars = self.variables.copy()
        vars.update(variables)

        for var in vars:
            if not VARIABLE_RE.match(var):
                msg = 'invalid variable name: "{0}"'
                raise SyntaxError(msg.format(token))

        def parentheses_replace(matchobj):
            inner_form = matchobj.group(1)
            inner_result = self._calculate(inner_form, vars)
            return six.text_type(inner_result).lower()

        replaces = True
        while replaces:
            form, replaces = PARENTHESES_RE.subn(parentheses_replace, form)

        if '(' in form or ')' in form:
            raise SyntaxError('improperly closed parentheses')

        return self._calculate(form, vars)

    def _calculate(self, form, vars):

        tokens = TOKENS_RE.findall(form)
        for i, token in enumerate(tokens):
            if DECIMAL_RE.match(token):
                tokens[i] = force_decimal(token)
            elif token in vars:
                tokens[i] = force_decimal(vars[token])
            elif token == 'true':
                tokens[i] = True
            elif token == 'false':
                tokens[i] = False
            elif token in ('none', 'null'):
                tokens[i] = None

        def get_previous_value(current_pos):
            previous_pos = current_pos - 1
            if previous_pos < 0:
                raise SyntaxError('invalid syntax')
            return tokens[previous_pos]

        result = Undefined
        for i, token in reversed(tuple(enumerate(tokens))):

            if result is Undefined:
                if (i == (len(tokens) - 1)
                        and not isinstance(token, six.string_types)):
                    result = token
                    continue
                else:
                    raise SyntaxError('invalid syntax')

            if not isinstance(token, six.string_types):
                continue

            if token == '+':
                try:
                    a = get_previous_value(i)
                except SyntaxError:
                    result = operator.pos(result)
                else:
                    result = operator.add(a, result)
            elif token == '-':
                try:
                    a = get_previous_value(i)
                except SyntaxError:
                    result = operator.neg(result)
                else:
                    result = operator.sub(a, result)
            elif token == '*':
                a = get_previous_value(i)
                result = operator.mul(a, result)
            elif token in ('**', '^'):
                a = get_previous_value(i)
                result = operator.pow(a, result)
            elif token == '/':
                a = get_previous_value(i)
                result = operator.truediv(a, result)
            elif token == '//':
                a = get_previous_value(i)
                result = operator.floordiv(a, result)
            elif token == '%':
                a = get_previous_value(i)
                result = operator.mod(a, result)
            elif token == '<':
                a = get_previous_value(i)
                result = operator.lt(a, result)
            elif token == '<=':
                a = get_previous_value(i)
                result = operator.le(a, result)
            elif token in ('==', '='):
                a = get_previous_value(i)
                result = operator.eq(a, result)
            elif token in ('!=', '<>'):
                a = get_previous_value(i)
                result = operator.ne(a, result)
            elif token == '>':
                a = get_previous_value(i)
                result = operator.gt(a, result)
            elif token == '>=':
                a = get_previous_value(i)
                result = operator.ge(a, result)
            elif token == 'not':
                result = (not result)
            elif token == 'and':
                a = get_previous_value(i)
                result = (a  and result)
            elif token == 'or':
                a = get_previous_value(i)
                result = (a  or result)
            elif VARIABLE_RE.search(token):
                msg = 'unknown variable: "{0}"'
                raise SyntaxError(msg.format(token))
            else:
                msg = 'unknown operator: "{0}"'
                raise SyntaxError(msg.format(token))

        if result is Undefined:
            raise SyntaxError('invalid syntax')

        return result

