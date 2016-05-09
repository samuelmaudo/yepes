# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils import six
from django.utils.translation import ugettext as _

from yepes.apps import apps
from yepes.types import Undefined

Message = apps.get_model('newsletters', 'Message')
MessageImage = apps.get_model('newsletters', 'MessageImage')
MessageLink = apps.get_model('newsletters', 'MessageLink')
Newsletter = apps.get_model('newsletters', 'Newsletter')
Subscriber = apps.get_model('newsletters', 'Subscriber')


class ImageMixin(object):

    _image = Undefined
    image_field = 'image'
    require_image = False

    def get_image(self):
        if self._image is Undefined:

            image = None

            guid = self.kwargs.get('image_guid', self.request.GET.get('i'))
            name = self.kwargs.get('image_name')
            try:
                if guid:
                    image = MessageImage.objects.get(guid=guid)
                elif name:
                    image = MessageImage.objects.get(name=name)
            except MessageImage.DoesNotExist:
                msg = _('No {verbose_name} found matching the query.')
                kwargs = {'verbose_name': MessageImage._meta.verbose_name}
                raise Http404(msg.format(**kwargs))

            if image is None and self.require_image:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': MessageImage._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._image = image

        return self._image

    def get_context_data(self, **kwargs):
        context = super(ImageMixin, self).get_context_data(**kwargs)
        context['image'] = self.get_image()
        return context

    def get_queryset(self):
        qs = super(ImageMixin, self).get_queryset()
        if self.get_image():
            qs = qs.filter(**{self.image_field: self.get_image()})
        return qs


class LinkMixin(object):

    _link = Undefined
    link_field = 'link'
    require_link = False

    def get_link(self):
        if self._link is Undefined:

            link = None

            guid = self.kwargs.get('link_guid', self.request.GET.get('l'))
            url = self.kwargs.get('link_url', self.request.GET.get('u'))
            try:
                if guid:
                    link = MessageLink.objects.get(guid=guid)
                elif url:
                    link = MessageLink.objects.get(url=url)
            except MessageLink.DoesNotExist:
                msg = _('No {verbose_name} found matching the query.')
                kwargs = {'verbose_name': MessageLink._meta.verbose_name}
                raise Http404(msg.format(**kwargs))

            if link is None and self.require_link:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': MessageLink._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._link = link

        return self._link

    def get_context_data(self, **kwargs):
        context = super(LinkMixin, self).get_context_data(**kwargs)
        context['link'] = self.get_link()
        return context

    def get_queryset(self):
        qs = super(LinkMixin, self).get_queryset()
        if self.get_link():
            qs = qs.filter(**{self.link_field: self.get_link()})
        return qs


class MessageMixin(object):

    _message = Undefined
    message_field = 'message'
    require_message = False

    def get_message(self):
        if self._message is Undefined:

            message = None

            guid = self.kwargs.get('message_guid', self.request.GET.get('m'))
            slug = self.kwargs.get('message_slug')
            try:
                if guid:
                    message = Message.objects.get(guid=guid)
                elif slug:
                    message = Message.objects.get(slug=slug)
            except Message.DoesNotExist:
                msg = _('No {verbose_name} found matching the query.')
                kwargs = {'verbose_name': Message._meta.verbose_name}
                raise Http404(msg.format(**kwargs))

            if message is None and self.require_message:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': Message._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._message = message

        return self._message

    def get_context_data(self, **kwargs):
        context = super(MessageMixin, self).get_context_data(**kwargs)
        context['message'] = self.get_message()
        return context

    def get_queryset(self):
        qs = super(MessageMixin, self).get_queryset()
        if self.get_message():
            qs = qs.filter(**{self.message_field: self.get_message()})
        return qs


class NewsletterMixin(object):

    _newsletter = Undefined
    newsletter_field = 'newsletter'
    require_newsletter = False

    def get_newsletter(self):
        if self._newsletter is Undefined:

            newsletter = None

            guid = self.kwargs.get('newsletter_guid', self.request.GET.get('n'))
            slug = self.kwargs.get('newsletter_slug')
            try:
                if guid:
                    newsletter = Newsletter.objects.get(guid=guid)
                elif slug:
                    newsletter = Newsletter.objects.get(slug=slug)
            except Newsletter.DoesNotExist:
                msg = _('No {verbose_name} found matching the query.')
                kwargs = {'verbose_name': Newsletter._meta.verbose_name}
                raise Http404(msg.format(**kwargs))

            if newsletter is None and self.require_newsletter:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': Newsletter._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._newsletter = newsletter

        return self._newsletter

    def get_context_data(self, **kwargs):
        context = super(NewsletterMixin, self).get_context_data(**kwargs)
        context['newsletter'] = self.get_newsletter()
        return context

    def get_queryset(self):
        qs = super(NewsletterMixin, self).get_queryset()
        if self.get_newsletter():
            qs = qs.filter(**{self.newsletter_field: self.get_newsletter()})
        return qs


class SubscriberMixin(object):

    _subscriber = Undefined
    subscriber_field = 'subscriber'
    require_subscriber = False

    def get_subscriber(self):
        if self._subscriber is Undefined:

            subscriber = None

            guid = self.kwargs.get('subscriber_guid', self.request.GET.get('s'))
            address = self.kwargs.get('subscriber_email', self.request.GET.get('e'))
            try:
                if guid:
                    subscriber = Subscriber.objects.get(guid=guid)
                elif address:
                    subscriber = Subscriber.objects.get(email_address=address)
            except Subscriber.DoesNotExist:
                msg = _('No {verbose_name} found matching the query.')
                kwargs = {'verbose_name': Subscriber._meta.verbose_name}
                raise Http404(msg.format(**kwargs))

            if subscriber is None and self.require_subscriber:
                msg = _('You must specify a {verbose_name}.')
                kwargs = {'verbose_name': Subscriber._meta.verbose_name}
                raise ImproperlyConfigured(msg.format(**kwargs))

            self._subscriber = subscriber

        return self._subscriber

    def get_context_data(self, **kwargs):
        context = super(SubscriberMixin, self).get_context_data(**kwargs)
        context['subscriber'] = self.get_subscriber()
        return context

    def get_queryset(self):
        qs = super(SubscriberMixin, self).get_queryset()
        if self.get_subscriber():
            qs = qs.filter(**{self.subscriber_field: self.get_subscriber()})
        return qs

