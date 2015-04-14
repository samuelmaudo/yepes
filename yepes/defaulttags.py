# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from functools import update_wrapper
import hashlib

from django.core.cache import cache
from django.template import (
    Context, Library, Variable,
    TemplateSyntaxError, VariableDoesNotExist,
)
from django.utils import six
from django.utils.decorators import classonlymethod
from django.utils.encoding import force_bytes, force_str, force_text
from django.utils.http import urlquote
from django.utils.six.moves import range
from django.utils.text import Truncator

from yepes.conf import settings
from yepes.template import (
    AssignTag,
    DoubleTag,
    InclusionTag,
    TagSyntaxError,
)
from yepes.utils.minifier import html_minifier
from yepes.utils.phased import (
    backup_csrf_token,
    flatten_context,
    pickle_context,
    SECRET_DELIMITER,
)

register = Library()


## {% build_full_url location **kwargs[ as variable_name] %} ##################


class BuildFullUrlTag(AssignTag):
    """
    Adds the scheme name and the authority part (domain and subdomain) to the
    given absolute path.
    """
    assign_var = False

    def process(self, location, **kwargs):
        from yepes.urlresolvers import build_full_url
        return build_full_url(location, **kwargs)

register.tag('build_full_url', BuildFullUrlTag.as_tag())


## {% cache expire_time fragment_name *vary_on %} ##############################


class CacheTag(DoubleTag):
    """
    Caches the contents of a template fragment for a given amount of time.

    Usage::

    {% cache expire_time fragment_name %}
    .. some expensive processing ..
    {% endcache %}

    This tag also supports varying by a list of arguments::

    {% cache expire_time fragment_name var1 var2 .. %}
    .. some expensive processing ..
    {% endcache %}

    Each unique set of arguments will result in a unique cache entry.

    """
    @classmethod
    def get_syntax(cls, tag_name='tag_name'):
        open_tag = '{{% {0} expire_time fragment_name *vary_on %}}'
        close_tag = '{{% end{0} %}}'
        return ''.join((open_tag, '...', close_tag)).format(tag_name)

    @classonlymethod
    def parse_arguments(cls, parser, bits):
        if len(bits) < 2:
            raise TagSyntaxError(cls, cls.tag_name)

        fragment_name = bits.pop(1)
        args, kwargs = super(CacheTag, cls).parse_arguments(parser, bits)
        if kwargs:
            raise TagSyntaxError(cls, cls.tag_name)

        args.insert(1, fragment_name)
        return (args, kwargs)

    def process(self, expire_time, fragment_name, *vary_on):
        try:
            expire_time = int(expire_time)
        except (ValueError, TypeError):
            msg = "'{0}' tag got a non-integer timeout value: {0!r}"
            raise TemplateSyntaxError(msg.format(self.tag_name, expire_time))

        # Build a key for this fragment and all vary-on's.
        key = ':'.join(urlquote(v) for v in vary_on)
        key = hashlib.md5(force_bytes(key)).hexdigest()
        cache_key = 'template.cache.{0}.{1}'.format(fragment_name, key)

        # Get fragment's value from cache or render it.
        value = cache.get(cache_key)
        if value is None:
            value = self.nodelist.render(self.context)
            value = html_minifier.minify(value)
            cache.set(cache_key, value, expire_time)

        return value

register.tag('cache', CacheTag.as_tag())


## {% full_url view_name *args **kwargs[ as variable_name] %} #################


class FullUrlTag(AssignTag):
    """
    Returns a full URL matching given view with its parameters.

    This is a way to define links that aren't tied to a particular URL
    configuration::

    {% full_url 'path.to.some_view' %}

    The first argument is a path to a view. It can be an absolute Python path
    or just ``app_name.view_name`` without the project name if the view is
    located inside the project.

    Other arguments are space-separated values that will be filled in place of
    positional and keyword arguments in the URL. Don't mix positional and
    keyword arguments.

    All arguments for the URL should be present.

    For example if you have a view ``app_name.client`` taking client's id and
    the corresponding line in a URLconf looks like this::

    ('^client/(\d+)/$', 'app_name.client')

    and this app's URLconf is included into the project's URLconf under some
    path::

    ('^clients/', include('project_name.app_name.urls'))

    then in a template you can create a link for a certain client like this::

    {% full_url 'app_name.client' client.id %}

    The URL will look like ``http://example.org/clients/client/123/``.

    The first argument can also be a named URL instead of the Python path to
    the view callable. For example if the URLconf entry looks like this::

    url('^client/(\d+)/$', name='client-detail-view')

    then in the template you can use::

    {% full_url 'client-detail-view' client.id %}

    There is even another possible value type for the first argument. It can be
    the name of a template variable that will be evaluated to obtain the view
    name or the URL name, e.g.::

    {% with view_path='app_name.client' %}
    {% full_url view_path client.id %}
    {% endwith %}

    or,

    {% with url_name='client-detail-view' %}
    {% full_url url_name client.id %}
    {% endwith %}

    """
    assign_var = False

    def process(self, view_name, *args, **kwargs):
        from django.core.urlresolvers import NoReverseMatch
        from yepes.urlresolvers import full_reverse
        scheme = kwargs.pop('scheme', None)
        domain = kwargs.pop('domain', None)
        subdomain = kwargs.pop('subdomain', None)

        # Try to look up the URL twice: once given the view name, and again
        # relative to what we guess is the "main" app. If they both fail,
        # re-raise the NoReverseMatch unless we're using the
        # {% full_url ... as var %} construct in which cause return nothing.
        url = ''
        try:
            url = full_reverse(view_name, args=args, kwargs=kwargs,
                               current_app=self.context.current_app,
                               scheme=scheme, domain=domain,
                               subdomain=subdomain)
        except NoReverseMatch as e:
            if settings.SETTINGS_MODULE:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                try:
                    url = full_reverse(project_name + '.' + view_name,
                                       args=args, kwargs=kwargs,
                                       current_app=self.context.current_app,
                                       scheme=scheme, domain=domain,
                                       subdomain=subdomain)
                except NoReverseMatch:
                    if not self.target_var:
                        # Re-raise the original exception, not the one with
                        # the path relative to the project. This makes a
                        # better error message.
                        raise e
            else:
                if not self.target_var:
                    raise e

        return url

register.tag('full_url', FullUrlTag.as_tag())


## {% pagination[ paginator[ page_obj]] **kwargs %} ###########################


class PaginationTag(InclusionTag):

    template = 'partials/pagination.html'

    def process(self, paginator=None, page_obj=None, **kwargs):
        if paginator is None:
            if 'paginator' in self.context:
                paginator = self.context['paginator']
            else:
                return ''

        if page_obj is None:
            if 'page_obj' in self.context:
                page_obj = self.context['page_obj']
            else:
                return ''

        if paginator.num_pages < 2:
            return ''

        num_pages = paginator.num_pages
        delimiter = page_obj.number - 1
        visible_pages = int(kwargs.pop('visible_pages', 7))
        previous_pages = int((visible_pages - 1) / 2)
        if delimiter < previous_pages:
            previous_pages = delimiter
        next_pages = visible_pages - previous_pages
        if delimiter + next_pages > num_pages:
            next_pages = num_pages - delimiter

        visible_page_range = list(
            range(page_obj.number - previous_pages,
                   page_obj.number + next_pages))

        display_gaps = kwargs.pop('display_gaps', 'False')
        if display_gaps in ('t', 'True', '1'):
            display_gaps = True
        if display_gaps in ('f', 'False', '0'):
            display_gaps = False
        else:
            display_gaps = bool(display_gaps)

        if display_gaps and len(visible_page_range) > 4:
            if visible_page_range[0] != 1:
                visible_page_range[0] = 1
                visible_page_range[1] = None
            if visible_page_range[-1] != num_pages:
                visible_page_range[-1] = num_pages
                visible_page_range[-2] = None

        query_string = '?' + '&'.join(
                '{0}={1}'.format(urlquote(k), urlquote(v))
                for k, v
                in six.iteritems(kwargs))

        context = self.get_new_context()
        context.update({
            'kwargs': kwargs,
            'next_page_number': page_obj.number + 1,
            'num_pages': num_pages,
            'page_number': page_obj.number,
            'page_obj': page_obj,
            'paginator': paginator,
            'previous_page_number': page_obj.number - 1,
            'query_string': query_string,
            'visible_page_range': visible_page_range,
        })
        return self.get_content(context)

register.tag('pagination', PaginationTag.as_tag())


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

