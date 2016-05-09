# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.template import Context, Template

from yepes.loading import LazyModel

MessageImage = LazyModel('newsletters', 'MessageImage')
MessageLink = LazyModel('newsletters', 'MessageLink')

IMAGE_RE = re.compile(r"\{% image_url '([^']*)' %\}")
LINK_RE = re.compile(r"\{% link_url '([^']*)' %\}")


def prerender(source, context=None):
    ctxt = Context({'prerendering': True})
    load = '{% load newsletters %}\n'
    if context is not None:
        ctxt.update(context)

    prerendered = Template(load + source).render(ctxt)

    image_names = set()
    def image_collector(matchobj):
        image_names.add(matchobj.group(1))
        return matchobj.group(0)
    IMAGE_RE.sub(image_collector, prerendered)

    image_guids = dict(MessageImage.objects.filter(
        name__in=image_names,
    ).values_list(
        'name',
        'guid',
    ))
    def image_replacement(matchobj):
        guid = image_guids.get(matchobj.group(1))
        return "{{% prerendered_image '{0}' %}}".format(guid) if guid else ''
    prerendered = IMAGE_RE.sub(image_replacement, prerendered)

    link_urls = set()
    def link_collector(matchobj):
        link_urls.add(matchobj.group(1))
        return matchobj.group(0)
    LINK_RE.sub(link_collector, prerendered)

    link_guids = dict(MessageLink.objects.filter(
        url__in=link_urls,
    ).values_list(
        'url',
        'guid',
    ))

    new_links = [
        MessageLink(url=url)
        for url in link_urls
        if url not in link_guids
    ]
    if new_links:
        MessageLink.objects.bulk_create(new_links)
        for link in new_links:
            link_guids[link.url] = link.guid

    def link_replacement(matchobj):
        guid = link_guids.get(matchobj.group(1))
        return "{{% prerendered_link '{0}' %}}".format(guid)
    prerendered = LINK_RE.sub(link_replacement, prerendered)

    return prerendered


def render(template_string, context=None):
    ctxt = Context()
    load = '{% load newsletters %}\n'
    if context is not None:
        ctxt.update(context)

    return Template(load + template_string).render(ctxt)

