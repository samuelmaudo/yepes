# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from functools import update_wrapper
import inspect

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.template.base import (
    kwarg_re as KWARG_RE,
    Node,
    Template, TemplateSyntaxError,
    TOKEN_BLOCK, TOKEN_COMMENT, TOKEN_TEXT, TOKEN_VAR,
    VariableDoesNotExist,
)
from django.template.context import Context
from django.template.loader import get_template, select_template
from django.utils import six
from django.utils.decorators import classonlymethod
from django.utils.encoding import force_str, smart_bytes
from django.utils.itercompat import is_iterable
from django.utils.safestring import mark_safe

TOKEN_LITERALS = {
    TOKEN_BLOCK: '{{% {0} %}}',
    TOKEN_VAR: '{{{{ {0} }}}}',
    TOKEN_COMMENT: '{{# {0} #}}',
    TOKEN_TEXT: '{0}',
}


class TagSyntaxError(TemplateSyntaxError):

    def __init__(self, tag, tag_name='<tag_name>'):
        msg = 'Correct syntax is {0}'.format(tag.get_syntax(tag_name))
        super(TagSyntaxError, self).__init__(msg)


class Sandbox(object):

    def __init__(self, tag, context):
        self.tag = tag
        self.context = context

    def __getattr__(self, name):
        return getattr(self.tag, name)

    def get_content(self, context=None):
        c = getattr(self.tag, 'content', None)
        if c is not None:
            return c
        nl = getattr(self.tag, 'nodelist', None)
        if nl is not None:
            return nl.render(context or self.context)

    def get_new_context(self):
        return Context(**{
            'autoescape': self.context.autoescape,
            'current_app': self.context.current_app,
            'use_l10n': self.context.use_l10n,
            'use_tz': self.context.use_tz
        })

    def resolve_args(self):
        args = []
        for arg in self.args:
            try:
                arg = arg.resolve(self.context)
            except AttributeError:
                pass
            except VariableDoesNotExist:
                msg = "'{0}' tag got an unknown variable: {1!r}"
                raise TemplateSyntaxError(msg.format(self.tag_name, arg))

            args.append(arg)

        return args

    def resolve_kwargs(self):
        kwargs = {}
        for key, value in six.iteritems(self.kwargs):
            try:
                value = value.resolve(self.context)
            except AttributeError:
                pass
            except VariableDoesNotExist:
                msg = "'{0}' tag got an unknown variable: {1!r}"
                raise TemplateSyntaxError(msg.format(self.tag_name, value))

            kwargs[smart_bytes(key, 'ascii')] = value

        return kwargs

    def run(self, func):
        args = self.resolve_args()
        kwargs = self.resolve_kwargs()
        return func(self, *args, **kwargs)

    def super_proccess(self, *args, **kwargs):
        func = self.tag.get_super_process_function()
        return func(self, *args, **kwargs)


class SingleTag(Node):

    sandbox_class = Sandbox

    def __init__(self, **kwargs):
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    def __repr__(self):
        return force_str('<{0}>'.format(self.__class__.__name__))

    @classonlymethod
    def as_tag(cls, **initkwargs):

        def tag(parser, token):
            initkwargs.update(cls.parse_token(parser, token))
            node = cls(**initkwargs)
            node.validate()
            return node

        update_wrapper(tag, cls, updated=())
        return tag

    @classmethod
    def get_process_arguments(cls):
        return inspect.getargspec(cls.get_process_function())

    @classmethod
    def get_process_function(cls):
        for base in cls.__mro__:
            func = base.__dict__.get('process')
            if func is not None:
                return func

    @classmethod
    def get_super_process_function(cls):
        for base in cls.__mro__[1:]:
            func = base.__dict__.get('process')
            if func is not None:
                return func

    @classmethod
    def get_syntax(cls, tag_name='tag_name'):
        syntax = []
        args, varargs, keywords, defaults = cls.get_process_arguments()
        num_args = len(args)
        num_defaults = len(defaults or ())
        for i, arg_name in enumerate(args, 1):
            if i > 1:
                j = num_args - i
                if j >= num_defaults:
                    syntax.append(' {0}'.format(arg_name))
                else:
                    syntax.append('[ {0}'.format(arg_name))
                    if j == 0:
                        syntax.append(']' * num_defaults)

        if varargs:
            syntax.append(' *{0}'.format(varargs))

        if keywords:
            syntax.append(' **{0}'.format(keywords))

        return '{{% {0}{1} %}}'.format(tag_name, ''.join(syntax))

    @classonlymethod
    def parse_arguments(cls, parser, tag_name, bits):
        args = []
        kwargs = {}
        for bit in bits:

            match = KWARG_RE.match(bit)
            if not match:
                msg = '"{0}" is not a valid argument.'
                raise TemplateSyntaxError(msg.format(bit))

            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

        return (args, kwargs)

    @classonlymethod
    def parse_token(cls, parser, token):
        bits = token.split_contents()
        tag_name = bits[0]
        args, kwargs = cls.parse_arguments(parser, tag_name, bits[1:])
        return {
            'tag_name': tag_name,
            'args': args,
            'kwargs': kwargs,
        }

    def process(self):
        pass

    def render(self, context):
        sandbox = self.sandbox_class(self, context)
        func = self.get_process_function()
        return sandbox.run(func)

    def validate(self):
        func = self.get_process_function()
        try:
            inspect.getcallargs(func, self, *self.args, **self.kwargs)
        except TypeError:
            raise TagSyntaxError(self, self.tag_name)


class AssignTag(SingleTag):

    assign_var = True
    target_var = None
    is_safe = False

    @classmethod
    def get_syntax(cls, tag_name='tag_name'):
        if cls.target_var or not cls.assign_var:
            suffix = '[ as variable_name]'
        else:
            suffix = ' as variable_name'

        syntax = super(AssignTag, cls).get_syntax(tag_name)
        return ''.join((syntax[:-3], suffix, syntax[-3:]))

    @classonlymethod
    def parse_token(cls, parser, token):
        bits = token.split_contents()
        target_var = cls.target_var
        if len(bits) > 2 and bits[-2] == 'as':
            target_var = bits[-1]
            bits = bits[:-2]

        tag_name = bits[0]
        args, kwargs = cls.parse_arguments(parser, tag_name, bits[1:])
        return {
            'tag_name': tag_name,
            'args': args,
            'kwargs': kwargs,
            'target_var': target_var,
        }

    def render(self, context):
        value = super(AssignTag, self).render(context)
        if self.is_safe:
            value = mark_safe(value)
        if self.target_var is not None:
            context[self.target_var] = value
            return ''
        else:
            return value

    def validate(self):
        super(AssignTag, self).validate()
        if self.assign_var and not self.target_var:
            raise TagSyntaxError(self, self.tag_name)


class DoubleTag(SingleTag):

    literal_content = False

    @classmethod
    def get_syntax(cls, tag_name='tag_name'):
        open_tag = super(DoubleTag, cls).get_syntax(tag_name)
        close_tag = '{{% end{0} %}}'.format(tag_name)
        return ''.join((open_tag, '...', close_tag))

    @classonlymethod
    def parse_token(cls, parser, token):
        bits = token.split_contents()
        tag_name = bits[0]
        args, kwargs = cls.parse_arguments(parser, tag_name, bits[1:])

        if cls.literal_content:
            content = ''.join(cls.parse_literals(parser, tag_name))
            nodelist = None
        else:
            content = None
            nodelist = cls.parse_nodelist(parser, tag_name)

        return {
            'tag_name': tag_name,
            'args': args,
            'kwargs': kwargs,
            'content': content,
            'nodelist': nodelist,
        }

    @classonlymethod
    def parse_literals(cls, parser, tag_name):
        """
        Parse to the end of a phased block.

        This is different than ``Parser.parse()`` in that it does not generate
        ``Node`` objects; it simply yields tokens.

        """
        close_tag_name = 'end{0}'.format(tag_name)
        depth = 0
        token_literals = []
        while parser.tokens:

            token = parser.next_token()
            if token.token_type == TOKEN_BLOCK:
                if token.contents == tag_name:
                    depth += 1
                elif token.contents == close_tag_name:
                    depth -= 1

            if depth < 0:
                break

            literal = TOKEN_LITERALS[token.token_type].format(token.contents)
            token_literals.append(literal)

        if not parser.tokens and depth >= 0:
            parser.unclosed_block_tag((close_tag_name, ))

        return token_literals

    @classonlymethod
    def parse_nodelist(cls, parser, tag_name):
        nodelist = parser.parse(('end{0}'.format(tag_name), ))
        parser.delete_first_token()
        return nodelist


class InclusionTag(SingleTag):

    @classonlymethod
    def parse_token(cls, parser, token):
        bits = token.split_contents()
        tag_name = bits[0]
        args, kwargs = cls.parse_arguments(parser, tag_name, bits[1:])

        t = kwargs.pop('template', cls.template)
        if isinstance(t, Template):
            template = t
        elif isinstance(t, six.string_types):
            template = get_template(t)
        elif is_iterable(t):
            template = select_template(t)
        else:
            template = Template('')

        return {
            'tag_name': tag_name,
            'args': args,
            'kwargs': kwargs,
            'content': None,
            'nodelist': template.nodelist,
        }


class SingleObjectMixin(object):

    field_name = 'pk'
    model = None
    queryset = None

    def get_field_name(self):
        """
        Get the name of the field to be used to look up the object.
        """
        return self.field_name

    def get_object(self, queryset, value):
        """
        Fetches the object that the tag will return.
        """
        field_name = self.get_field_name()
        filters = {'{0}__exact'.format(field_name): value}
        return queryset.filter(**filters).first()

    def get_queryset(self):
        """
        Get the queryset to look an object up against.
        """
        if self.queryset is not None:
            return self.queryset.all()
        elif self.model is not None:
            return self.model._default_manager.get_queryset()
        else:
            msg = ("'{0}' is missing a queryset."
                   " Define '{0}.model', '{0}.queryset',"
                   " or override '{0}.get_queryset()'.")
            raise ImproperlyConfigured(msg.format(self.__class__.__name__))


class MultipleObjectMixin(object):

    field_name = 'pk'
    model = None
    queryset = None

    def get_field_name(self):
        """
        Get the name of the field to be used to filter the objects.
        """
        return self.field_name

    def get_object_list(self, queryset, values):
        """
        Fetches the list of objects that the tag will return.
        """
        if not values:
            return queryset

        field_name = self.get_field_name()
        filters = {'{0}__in'.format(field_name): values}
        records = {
            getattr(record, field_name): record
            for record
            in queryset.filter(**filters)
        }
        return [records.get(value) for value in values]

    def get_queryset(self):
        """
        Get the list of items for this tag. This must be an iterable, and may
        be a queryset (in which qs-specific behavior will be enabled).
        """
        if self.queryset is not None:
            queryset = self.queryset
            try:
                cloner = queryset._clone
            except AttributeError:
                return queryset
            else:
                return cloner()
        elif self.model is not None:
            return self.model._default_manager.get_queryset()
        else:
            msg = ("'{0}' is missing a queryset."
                   " Define '{0}.model', '{0}.queryset',"
                   " or override '{0}.get_queryset()'.")
            raise ImproperlyConfigured(msg.format(self.__class__.__name__))

