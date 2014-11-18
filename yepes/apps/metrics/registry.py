# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes.apps.registry import Registry
from yepes.apps.registry.fields import *


registry = Registry(namespace='metrics')
registry.register(
    'EXCLUDED_PARAMETERS',
    CommaSeparatedField(
        initial = (),
        label = _('Excluded Parameters'),
        required = False,
))
registry.register(
    'RECORD_PAGE_VIEWS',
    BooleanField(
        initial = False,
        label = _('Record Page Views'),
        required = False,
))
registry.register(
    'RECORD_VISITORS',
    BooleanField(
        initial = False,
        label = _('Record Visitors'),
        required = False,
))
registry.register(
    'RECORD_VISITS',
    BooleanField(
        initial = False,
        label = _('Record Visits'),
        required = False,
))
registry.register(
    'TRACKED_REQUEST_METHODS',
    CommaSeparatedField(
        initial = ('GET', 'POST'),
        label = _('Tracked Request Methods'),
        max_length = 63,
        required = True,
))
registry.register(
    'UNTRACKED_PATHS',
    CommaSeparatedField(
        initial = ('/admin', '/cache', '/media', '/static'),
        label = _('Untracked Paths'),
        required = False,
))
registry.register(
    'UNTRACKED_REFERRERS',
    CommaSeparatedField(
        initial = (),
        label = _('Untracked Referrers'),
        required = False,
))
registry.register(
    'UNTRACKED_USER_AGENTS',
    CommaSeparatedField(
        initial = (

            # GENERIC
            'agent', 'archiver', 'audit', 'bot', 'check', 'crawler', 'link',
            'monit', 'proxy', 'search', 'sniff', 'spider', 'test', 'valid',

            # HTTP CLIENTS
            'curl', 'httpclient', 'php', 'urllib', 'wget', 'winhttp',

            # SEARCH ENGINES
            # 'alexa' must not be listed here because 'Alexa Toolbar' would
            #   also matched.
            # 'baidu' must not be listed here because 'baidubrowser' would
            #   also matched. However, Baidu robots always include 'spider'
            #   in their user-agent string.
            'ask', 'bing', 'coccoc', 'google', 'nutch', 'topsy', 'yacy',
            'yahoo', 'yandex',

            # SOCIAL NETWORKS
            'facebook', 'pinterest', 'twit',

            # OTHERS
            'craft',        # netcraft.com
            'fetch',        # UnwindFetchor
            'integrity',    # Integrity
            'meta',         # MetaURI
            'nine',         # nineconnections.com
            'ning',         # NING
            'shop',         # ShopMania
            'shot',         # Browsershots
            'solver',       # urlresolver
            'zoom',         # Ezooms (SEOMoz bot)

        ),
        label = _('Untracked User-Agents'),
        required = False,
))
registry.register(
    'VISIT_TIMEOUT',
    IntegerField(
        initial = 60 * 30,
        label = _('Visit Timeout'),
        required = True,
))

