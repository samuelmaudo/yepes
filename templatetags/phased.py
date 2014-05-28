# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.template import (
    Context, Library, Variable,
    TemplateSyntaxError, VariableDoesNotExist,
)
from django.utils.decorators import classonlymethod
from django.utils.encoding import force_str, force_text
from django.utils.text import Truncator

from yepes.apps.phased.utils import (
    backup_csrf_token,
    flatten_context,
    pickle_context,
    second_pass_render,
    SECRET_DELIMITER,
)
from yepes.conf import settings
from yepes.defaulttags import CacheTag
from yepes.template import DoubleTag, TagSyntaxError

register = Library()


## {% phased[ with *var_names] %} ##############################################


class PhasedTag(DoubleTag):
    """
    Template tag to denote a template section to render a second time via
    a middleware.

    Usage::

        {% load phased_tags %}
        {% phased %}
            .. some content to be rendered a second time ..
        {% endphased %}

    You can pass it a list of context variable names to automatically
    save those variables for the second pass rendering of the template,
    e.g.::

        {% load phased_tags %}
        {% phased with 'comment_count' 'object' %}
            There are {{ comment_count }} comments for "{{ object }}".
        {% endphased %}

    Alternatively you can also set the ``PHASED_KEEP_CONTEXT`` setting to
    ``True`` to automatically keep the whole context for each phased block.

    Note: Lazy objects such as messages and csrf tokens aren't kept.

    """
    literal_content = True

    def __repr__(self):
        args = (
            self.__class__.__name__,
            Truncator(force_text(self.content)).chars(25, '...'),
        )
        return force_str("<{0}: '{1}'>".format(*args), errors='replace')

    @classmethod
    def get_syntax(cls, tag_name='tag_name'):
        return '{{% {0}[ with *var_names] %}}'.format(tag_name)

    @classonlymethod
    def parse_arguments(cls, parser, bits):
        args = []
        kwargs = {}
        if bits:

            if len(bits) == 1 or bits[0] != 'with':
                raise TagSyntaxError(cls, cls.tag_name)

            for var_name in bits[1:]:
                if (var_name.startswith(('"', "'"))
                        and var_name.endswith(var_name[0])):
                    args.append(var_name[1:-1])
                else:
                    args.append(var_name)

        return (args, kwargs)

    def process(self, *var_names):
        """
        Outputs the literal content of the phased block with pickled context,
        enclosed in a delimited block that can be parsed by the second pass
        rendering middleware.
        """
        # our main context
        storage = Context()

        # stash the whole context if needed
        if settings.PHASED_KEEP_CONTEXT:
            storage.update(flatten_context(self.context))

        # but check if there are variables specifically wanted
        for var_name in var_names:
            try:
                storage[var_name] = Variable(var_name).resolve(self.context)
            except VariableDoesNotExist:
                msg = "'{0}' tag got an unknown variable: {1!r}"
                raise TemplateSyntaxError(msg.format(self.tag_name, var_name))

        storage = backup_csrf_token(self.context, storage)

        # lastly return the pre phased template part
        return '{delimiter}{content}{pickled}{delimiter}'.format(
                content=self.content,
                delimiter=SECRET_DELIMITER,
                pickled=pickle_context(storage))

register.tag('phased', PhasedTag.as_tag())


## {% phasedcache expire_time fragment_name *vary_on %} ########################


class PhasedCacheTag(CacheTag):
    """
    Inherits from ``yepes.defaulttags.CacheTag``.

    This will cache the contents of a template fragment for a given amount
    of time and do a second pass render on the contents.

    Usage::

        {% load phased_tags %}
        {% phasedcache expire_time fragment_name %}
            .. some expensive processing ..
            {% phased %}
                .. some request specific stuff ..
            {% endphased %}
        {% endphasedcache %}

    This tag also supports varying by a list of arguments::

        {% load phased_tags %}
        {% phasedcache expire_time fragment_name var1 var2 .. %}
            .. some expensive processing ..
            {% phased %}
                .. some request specific stuff ..
            {% endphased %}
        {% endphasedcache %}

    Each unique set of arguments will result in a unique cache entry.
    The tag will take care that the phased tags are properly rendered.

    It requires usage of ``RequestContext`` and
    ``django.core.context_processors.request`` to be in the
    ``TEMPLATE_CONTEXT_PROCESSORS`` setting.

    """
    def render(self, context):
        content = super(PhasedCacheTag, self).render(context)
        return second_pass_render(context['request'], content)

register.tag('phasedcache', PhasedCacheTag.as_tag())

