# -*- coding:utf-8 -*-

from __future__ import division, unicode_literals

import hashlib
import sys

from django.core.cache import cache
from django.template import Context, Library, TemplateSyntaxError, Variable
from django.template.base import kwarg_re as KWARG_RE
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
from yepes.utils.minifier import minify_html
from yepes.utils.phased import (
    backup_csrf_token,
    flatten_context,
    pickle_context,
    SECRET_DELIMITER,
)

register = Library()


## {% build_full_url location **kwargs[ as variable_name] %} ###################


class BuildFullUrlTag(AssignTag):
    """
    Adds the scheme name and the authority part (domain and subdomain)
    to the given absolute path.
    """
    assign_var = False

    def process(self, location, **kwargs):
        from yepes.urlresolvers import build_full_url
        return build_full_url(location, **kwargs)

register.tag('build_full_url', BuildFullUrlTag.as_tag())


## {% cache expire_time fragment_name *vary_on %} ##############################


class CacheTag(DoubleTag):
    """
    Caches the contents of a template fragment for a given amount of
    time.

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
    @classonlymethod
    def parse_arguments(cls, parser, tag_name, bits):
        if len(bits) < 2:
            raise TagSyntaxError(cls, tag_name)

        fragment_name = bits.pop(1)
        args, kwargs = super(CacheTag, cls).parse_arguments(parser, tag_name, bits)
        if kwargs:
            raise TagSyntaxError(cls, tag_name)

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
            value = minify_html(value)
            cache.set(cache_key, value, expire_time)

        return value

register.tag('cache', CacheTag.as_tag())


## {% phased[ with *vars **new_vars] %} ########################################


class PhasedTag(DoubleTag):
    """
    Template tag to denote a template section to render a second time
    via a middleware.

    Usage::

        {% load phased_tags %}
        {% phased %}
            .. some content to be rendered a second time ..
        {% endphased %}

    You can pass it a list of context variables to automatically save
    those variables for the second pass rendering of the template, e.g.::

        {% load phased_tags %}
        {% phased with object comment_count=10 %}
            There are {{ comment_count }} comments for "{{ object }}".
        {% endphased %}

    Alternatively you can also set the ``PHASED_KEEP_CONTEXT`` setting
    to ``True`` to automatically keep the whole context for each
    phased  block.

    NOTE: Lazy objects such as messages and csrf tokens aren't kept.

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
        return '{{% {0}[ with *vars **new_vars] %}}...{{% end{0} %}}'.format(tag_name)

    @classonlymethod
    def parse_arguments(cls, parser, tag_name, bits):
        args = []
        kwargs = {}
        if bits:

            if len(bits) == 1 or bits[0] != 'with':
                raise TagSyntaxError(cls, tag_name)

            for bit in bits[1:]:
                match = KWARG_RE.match(bit)
                if not match:
                    msg = '"{0}" is not a valid argument.'
                    raise TemplateSyntaxError(msg.format(bit))

                name, value = match.groups()
                if name:
                    kwargs[name] = parser.compile_filter(value)
                else:
                    kwargs[value] = Variable(value)

        return (args, kwargs)

    def process(self, **variables):
        """
        Outputs the literal content of the phased block with pickled
        context, enclosed in a delimited block that can be parsed by
        the second pass rendering middleware.
        """
        # our main context
        storage = {}

        # stash the whole context if needed
        if settings.PHASED_KEEP_CONTEXT:
            storage.update(flatten_context(self.context))

        # but check if there are variables specifically wanted
        storage.update(variables)
        backup_csrf_token(self.context, storage)

        # lastly return the pre phased template part
        return '{delimiter}{content}{pickled}{delimiter}'.format(
                content=self.content,
                delimiter=SECRET_DELIMITER,
                pickled=pickle_context(storage))

register.tag('phased', PhasedTag.as_tag())


## {% replace string old new[ count][ as variable_name] %} #####################


class ReplaceTag(AssignTag):
    """
    Returns a copy of the ``string`` with all occurrences of substring
    ``old`` replaced by ``new``. If the optional argument ``count`` is
    given, only the first ``count`` occurrences are replaced.
    """
    assign_var = False

    def process(self, string, old, new, count=None):
        string = force_text(string)
        old = force_text(old)
        new = force_text(new)
        if count is None:
            return string.replace(old, new)
        else:
            return string.replace(old, new, count)

register.tag('replace', ReplaceTag.as_tag())


## {% url view_name *args **kwargs[ as variable_name] %} #######################


class UrlTag(AssignTag):
    """
    Returns an absolute URL matching given view with its parameters.

    This is a way to define links that aren't tied to a particular
    URL configuration::

    {% url 'path.to.some_view' %}

    The first argument is a path to a view. It can be an absolute
    Python path or just ``app_name.view_name`` without the project
    name if the view is located inside the project.

    Other arguments are space-separated values that will be filled in
    place of positional and keyword arguments in the URL. Don't mix
    positional and keyword arguments.

    All arguments for the URL should be present.

    For example if you have a view ``app_name.client`` taking client's
    id and the corresponding line in a URLconf looks like this::

    ('^client/(\d+)/$', 'app_name.client')

    and this app's URLconf is included into the project's URLconf
    under some path::

    ('^clients/', include('project_name.app_name.urls'))

    then in a template you can create a link for a certain client like
    this::

    {% url 'app_name.client' client.id %}

    The URL will look like ``http://example.org/clients/client/123/``.

    The first argument can also be a named URL instead of the Python
    path to the view callable. For example if the URLconf entry looks
    like this::

    url('^client/(\d+)/$', name='client-detail-view')

    then in the template you can use::

    {% url 'client-detail-view' client.id %}

    There is even another possible value type for the first argument.
    It can be the name of a template variable that will be evaluated
    to obtain the view name or the URL name, e.g.::

    {% with view_path='app_name.client' %}
    {% url view_path client.id %}
    {% endwith %}

    or,

    {% with url_name='client-detail-view' %}
    {% url url_name client.id %}
    {% endwith %}

    """
    assign_var = False

    def process(self, view_name, *args, **kwargs):
        from django.core.urlresolvers import reverse, NoReverseMatch

        try:
            current_app = self.context.request.current_app
        except AttributeError:
            try:
                current_app = self.context.current_app
            except AttributeError:
                try:
                    current_app = self.context.request.resolver_match.namespace
                except AttributeError:
                    current_app = None

        # Try to look up the URL twice: once given the view name, and
        # again relative to what we guess is the "main" app. If they
        # both fail, re-raise the NoReverseMatch unless we're using the
        # {% url ... as var %} construct in which cause return nothing.
        url = ''
        try:
            url = reverse(view_name, args=args, kwargs=kwargs,
                          current_app=current_app)
        except NoReverseMatch:
            exc_info = sys.exc_info()
            if settings.SETTINGS_MODULE:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                try:
                    url = reverse(project_name + '.' + view_name,
                                  args=args, kwargs=kwargs,
                                  current_app=current_app)
                except NoReverseMatch:
                    if not self.target_var:
                        # Re-raise the original exception, not the one with
                        # the path relative to the project. This makes a
                        # better error message.
                        six.reraise(*exc_info)
            else:
                if not self.target_var:
                    raise

        return url

register.tag('url', UrlTag.as_tag())


## {% full_url view_name *args **kwargs[ as variable_name] %} ##################


class FullUrlTag(UrlTag):
    """
    Returns a full URL matching given view with its parameters.

    This is a way to define links that aren't tied to a particular
    URL configuration::

    {% full_url 'path.to.some_view' %}

    The first argument is a path to a view. It can be an absolute
    Python path or just ``app_name.view_name`` without the project
    name if the view is located inside the project.

    Other arguments are space-separated values that will be filled in
    place of positional and keyword arguments in the URL. Don't mix
    positional and keyword arguments.

    All arguments for the URL should be present.

    For example if you have a view ``app_name.client`` taking client's
    id and the corresponding line in a URLconf looks like this::

    ('^client/(\d+)/$', 'app_name.client')

    and this app's URLconf is included into the project's URLconf
    under some path::

    ('^clients/', include('project_name.app_name.urls'))

    then in a template you can create a link for a certain client like
    this::

    {% full_url 'app_name.client' client.id %}

    The URL will look like ``http://example.org/clients/client/123/``.

    The first argument can also be a named URL instead of the Python
    path to the view callable. For example if the URLconf entry looks
    like this::

    url('^client/(\d+)/$', name='client-detail-view')

    then in the template you can use::

    {% full_url 'client-detail-view' client.id %}

    There is even another possible value type for the first argument.
    It can be the name of a template variable that will be evaluated
    to obtain the view name or the URL name, e.g.::

    {% with view_path='app_name.client' %}
    {% full_url view_path client.id %}
    {% endwith %}

    or,

    {% with url_name='client-detail-view' %}
    {% full_url url_name client.id %}
    {% endwith %}

    """
    def process(self, view_name, *args, **kwargs):
        from yepes.urlresolvers import build_full_url

        scheme = kwargs.pop('scheme', None)
        domain = kwargs.pop('domain', None)
        subdomain = kwargs.pop('subdomain', None)

        location = self.super_process(view_name, *args, **kwargs)

        return build_full_url(location,
                              scheme=scheme,
                              domain=domain,
                              subdomain=subdomain)

register.tag('full_url', FullUrlTag.as_tag())

