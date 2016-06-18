# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import base64
import re

from django.contrib.messages.storage.base import BaseStorage
from django.http import HttpRequest
from django.template.base import (
    COMMENT_TAG_START, COMMENT_TAG_END,
    Template,
    TemplateSyntaxError,
)
from django.template.context import BaseContext, RequestContext, Context
from django.utils import six
from django.utils.encoding import force_bytes, force_text
from django.utils.functional import Promise, LazyObject
from django.utils.six.moves import cPickle as pickle

from yepes.conf import settings

SECRET_DELIMITER = '{0} {1} {2}'.format(
        COMMENT_TAG_START,
        settings.PHASED_SECRET_DELIMITER,
        COMMENT_TAG_END)

PICKLED_CONTEXT_RE = re.compile(r'.*{0} context (.*) {1}.*'.format(
        COMMENT_TAG_START,
        COMMENT_TAG_END))

FORBIDDEN_CLASSES = (Promise, LazyObject, HttpRequest, BaseStorage)


def backup_csrf_token(context, storage=None):
    """
    Get the CSRF token and convert it to a string (since it's lazy).
    """
    if storage is None:
        storage = Context()

    token = context.get('csrf_token', 'NOTPROVIDED')
    storage['csrf_token'] = force_bytes(token)
    return storage


def flatten_context(context, remove_lazy=True):
    """
    Creates a dictionary from a ``Context`` instance by traversing its dicts
    list. Can remove unwanted subjects from the result, e.g. lazy objects.
    """
    flat_context = {}

    def _flatten(context):
        if isinstance(context, dict):
            for k, v in six.iteritems(context):
                if isinstance(context, BaseContext):
                    _flatten(context)
                else:
                    flat_context[k] = v
        elif isinstance(context, BaseContext):
            for context_dict in context.dicts:
                _flatten(context_dict)

    # traverse the passed context and update the dictionary accordingly
    _flatten(context)

    if remove_lazy:
        only_allowed = lambda dic: not isinstance(dic[1], FORBIDDEN_CLASSES)
        return dict(filter(only_allowed, six.iteritems(flat_context)))
    else:
        return flat_context


def pickle_context(context, template=None):
    """
    Pickle the given ``Context`` instance and do a few optimizations before.
    """
    if not isinstance(context, BaseContext):
        raise TemplateSyntaxError('Phased context is not a Context instance')

    context = flatten_context(context)
    context.pop('False', None)
    context.pop('None', None)
    context.pop('True', None)

    pickled_context = base64.standard_b64encode(
            pickle.dumps(context, protocol=pickle.HIGHEST_PROTOCOL))

    if template is not None:
        return template.format(context=pickle_context)
    else:
        return '{0} context {1} {2}'.format(
                COMMENT_TAG_START,
                pickled_context,
                COMMENT_TAG_END)


def restore_csrf_token(request, storage=None):
    """
    Given the request and a the context used during the second render phase,
    this wil check if there is a CSRF cookie and restores if needed, to
    counteract the way the CSRF framework invalidates the CSRF token after
    each request/response cycle.
    """
    if storage is None:
        storage = {}

    try:
        request.META['CSRF_COOKIE'] = request.COOKIES[settings.CSRF_COOKIE_NAME]
    except KeyError:
        csrf_token = storage.get('csrf_token', None)
        if csrf_token:
            request.META['CSRF_COOKIE'] = csrf_token

    return storage


def second_pass_render(request, content):
    """
    Split on the secret delimiter and render the phased blocks.
    """
    content = force_text(content)
    result = []
    for index, bit in enumerate(content.split(SECRET_DELIMITER)):
        if index % 2:
            template = Template(bit)
        else:
            result.append(bit)
            continue

        csrf_token = restore_csrf_token(request, unpickle_context(bit))
        context = RequestContext(request, csrf_token)
        try:
            rendered = template.render(context)
        except TemplateSyntaxError:
            # For example, in debug pages.
            return content

        if SECRET_DELIMITER in rendered:
            rendered = second_pass_render(request, rendered)

        result.append(rendered)

    return force_bytes(''.join(result))


def unpickle_context(content, pattern=None):
    """
    Unpickle the context from the given content string or return ``None``.
    """
    if pattern is None:
        pattern = PICKLED_CONTEXT_RE

    match = pattern.search(content)
    if match is not None:
        return pickle.loads(base64.standard_b64decode(match.group(1)))
    else:
        return None

