# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from decimal import Decimal as dec
import operator
import re

from django.utils import six
from django.utils.encoding import force_str, force_text
from django.utils.encoding import python_2_unicode_compatible

from yepes.exceptions import MissingAttributeError
from yepes.types.undefined import Undefined
from yepes.utils.decimals import force_decimal
from yepes.utils.properties import cached_property

__all__ = ('Formula', )

DECIMAL_RE = re.compile(r'([0-9]|[0-9]+[.,][0-9]*|[.,][0-9]+)')
PARENTHESES_RE = re.compile(r'\(([^()]*)\)')
TOKENS_RE = re.compile(r'([-]|[+]|[._a-zA-Z0-9]+|[^ ]+)')
VARIABLE_RE = re.compile(r'[_a-zA-Z][_a-zA-Z0-9]*')


@python_2_unicode_compatible
class Formula(object):

    constants = {
        'true': True,
        'false': False,
        'none': None,
        'null': None,
    }
    unary_operators = {
        '+': operator.pos,
        '-': operator.neg,
        'not': operator.not_,
    }
    binary_operators = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '**': operator.pow,
        '^': operator.pow,
        '/': operator.truediv,
        '//': operator.floordiv,
        '%': operator.mod,
        '<': operator.lt,
        '<=': operator.le,
        '=': operator.eq,
        '==': operator.eq,
        '!=': operator.ne,
        '<>': operator.ne,
        '>': operator.gt,
        '>=': operator.ge,
        'and': (lambda a, b: a and b),
        'or': (lambda a, b: a or b),
    }

    @cached_property
    def keywords(self):
        words = set(self.constants)
        words.update(op for op in self.unary_operators if op.islower())
        words.update(op for op in self.binary_operators if op.islower())
        return words

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
            self.variables[name] = value

    def __repr__(self):
        args = (
            self.__class__.__name__,
            self.formula,
        )
        return force_str('<{0}: {1}>'.format(*args))

    def __str__(self):
        return self.formula

    def __bool__(self):
        return (len(self.formula) > 0)

    def __nonzero__(self):
        return self.__bool__()

    def calculate(self, **variables):
        form = self.formula
        vars = self.variables.copy()
        vars.update(variables)
        for name, value in six.iteritems(vars):
            if not self.validate_variable(name):
                msg = 'invalid variable name: "{0}"'
                raise SyntaxError(msg.format(token))

            if isinstance(value, (six.integer_types, float)):
                vars[name] = force_decimal(value)

        def parentheses_replace(matchobj):
            inner_form = matchobj.group(1)
            inner_result = self._calculate(inner_form, vars)
            return six.text_type(inner_result).lower()

        replaces = 1
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
                tokens[i] = vars[token]
            elif token in self.constants:
                tokens[i] = self.constants[token]

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

            if token in self.binary_operators:
                try:
                    a = get_previous_value(i)
                except SyntaxError as error:
                    if token in self.unary_operators:
                        op = self.unary_operators[token]
                        result = op(result)
                    else:
                        raise error
                else:
                    op = self.binary_operators[token]
                    result = op(a, result)

            elif token in self.unary_operators:
                op = self.unary_operators[token]
                result = op(result)
                continue
            elif self.validate_variable(token):
                msg = 'unknown variable: "{0}"'
                raise SyntaxError(msg.format(token))
            else:
                msg = 'unknown op: "{0}"'
                raise SyntaxError(msg.format(token))

        if result is Undefined:
            raise SyntaxError('invalid syntax')

        return result

    def test(self, *variables):
        form = self.formula
        if variables:
            vars = {
                var: dec('1')
                for var
                in variables
            }
        else:
            tokens = TOKENS_RE.findall(form)
            vars = {
                token: dec('1')
                for token
                in tokens
                if self.validate_variable(token)
            }
        self.calculate(**vars)

    def validate(self, *variables):
        try:
            self.test(*variables)
        except SyntaxError:
            return False
        else:
            return True

    def validate_variable(self, name):
        return (VARIABLE_RE.search(name) is not None
                and name not in self.keywords)

