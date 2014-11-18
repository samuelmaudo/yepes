# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.cache import get_cache
from django.template.base import Library

from yepes.loading import get_model
from yepes.template import SingleTag
from yepes.urlresolvers import full_reverse
from yepes.types import Undefined

MessageImage = get_model('newsletters', 'MessageImage')
MessageImageManager = MessageImage._default_manager
MessageLink = get_model('newsletters', 'MessageLink')
MessageLinkManager = MessageLink._default_manager

IMAGE_CACHE = get_cache('django.core.cache.backends.locmem.LocMemCache', **{
    'LOCATION': 'yepes.templatetags.newsletters.image_url',
    'TIMEOUT': 600,
})
LINK_CACHE = get_cache('django.core.cache.backends.locmem.LocMemCache', **{
    'LOCATION': 'yepes.templatetags.newsletters.link_url',
    'TIMEOUT': 600,
})

register = Library()


## {% image_url name %} ########################################################


class ImageUrlTag(SingleTag):

    def process(self, name):
        if self.context.get('prerendering'):
            return "{{% {0} '{1}' %}}".format(self.tag_name, name)

        image = IMAGE_CACHE.get(name, Undefined)
        if image is Undefined:
            image = MessageImageManager.filter(name=name).first()
            IMAGE_CACHE.set(name, image)

        if image is None:
            return ''

        subscriber = self.context.get('subscriber')
        message = self.context.get('message')
        kwargs = {'image_guid': image.guid}
        if subscriber is not None and message is not None:
            kwargs['subscriber_guid'] = subscriber.guid
            kwargs['message_guid'] = message.guid

        return full_reverse('image', kwargs=kwargs)

register.tag('image_url', ImageUrlTag.as_tag())


## {% link_url url %} ##########################################################


class LinkUrlTag(SingleTag):

    def process(self, url):
        if self.context.get('prerendering'):
            return "{{% {0} '{1}' %}}".format(self.tag_name, url)

        link = LINK_CACHE.get(url)
        if link is None:
            link, __ = MessageLinkManager.get_or_create(url=url)
            LINK_CACHE.set(url, link)

        subscriber = self.context.get('subscriber')
        message = self.context.get('message')

        kwargs = {'link_guid': link.guid}
        if subscriber is not None and message is not None:
            kwargs['subscriber_guid'] = subscriber.guid
            kwargs['message_guid'] = message.guid

        return full_reverse('link', kwargs=kwargs)

register.tag('link_url', LinkUrlTag.as_tag())


## {% message_url %} ###########################################################


class MessageUrlTag(SingleTag):

    def process(self):
        if self.context.get('prerendering'):
            return "{{% {0} %}}".format(self.tag_name)

        subscriber = self.context.get('subscriber')
        message = self.context.get('message')
        if message is None:
            return ''

        kwargs = {'message_guid': message.guid}
        if subscriber is not None:
            kwargs['subscriber_guid'] = subscriber.guid

        return full_reverse('message', kwargs=kwargs)

register.tag('message_url', MessageUrlTag.as_tag())


## {% prerendered_image guid %} ################################################


class PrerenderedImageTag(SingleTag):

    def process(self, guid):
        if self.context.get('prerendering'):
            return "{{% {0} '{1}' %}}".format(self.tag_name, guid)

        subscriber = self.context.get('subscriber')
        message = self.context.get('message')
        kwargs = {'image_guid': guid}
        if subscriber is not None and message is not None:
            kwargs['subscriber_guid'] = subscriber.guid
            kwargs['message_guid'] = message.guid

        return full_reverse('image', kwargs=kwargs)

register.tag('prerendered_image', PrerenderedImageTag.as_tag())


## {% prerendered_link guid %} ##########################################################


class PrerenderedLinkTag(SingleTag):

    def process(self, guid):
        if self.context.get('prerendering'):
            return "{{% {0} '{1}' %}}".format(self.tag_name, guid)

        subscriber = self.context.get('subscriber')
        message = self.context.get('message')
        kwargs = {'link_guid': guid}
        if subscriber is not None and message is not None:
            kwargs['subscriber_guid'] = subscriber.guid
            kwargs['message_guid'] = message.guid

        return full_reverse('link', kwargs=kwargs)

register.tag('prerendered_link', PrerenderedLinkTag.as_tag())


## {% profile_url %} ###########################################################


class ProfileUrlTag(SingleTag):

    def process(self):
        if self.context.get('prerendering'):
            return "{{% {0} %}}".format(self.tag_name)

        subscriber = self.context.get('subscriber')
        newsletter = self.context.get('newsletter')
        message = self.context.get('message')
        if subscriber is None:
            return ''

        kwargs = {'subscriber_guid': subscriber.guid}
        if newsletter is not None:
            kwargs['newsletter_guid'] = newsletter.guid
        if message is not None:
            kwargs['message_guid'] = message.guid

        return full_reverse('profile', kwargs=kwargs)

register.tag('profile_url', ProfileUrlTag.as_tag())


## {% resubscription_url %} ####################################################


class ResubscriptionUrlTag(SingleTag):

    def process(self):
        if self.context.get('prerendering'):
            return "{{% {0} %}}".format(self.tag_name)

        subscriber = self.context.get('subscriber')
        newsletter = self.context.get('newsletter')
        if subscriber is None or newsletter is None:
            return ''

        return full_reverse('resubscription', kwargs={
            'subscriber_guid': subscriber.guid,
            'newsletter_guid': newsletter.guid,
        })

register.tag('resubscription_url', ResubscriptionUrlTag.as_tag())


## {% subscription_url %} ######################################################


class SubscriptionUrlTag(SingleTag):

    def process(self):
        if self.context.get('prerendering'):
            return "{{% {0} %}}".format(self.tag_name)

        subscriber = self.context.get('subscriber')
        newsletter = self.context.get('newsletter')

        kwargs = {}
        if subscriber is not None:
            kwargs['subscriber_guid'] = subscriber.guid
        if newsletter is not None:
            kwargs['newsletter_guid'] = newsletter.guid

        return full_reverse('subscription', kwargs=kwargs)

register.tag('subscription_url', SubscriptionUrlTag.as_tag())


## {% unsubscription_url %} ####################################################


class UnsubscriptionUrlTag(SingleTag):

    def process(self):
        if self.context.get('prerendering'):
            return "{{% {0} %}}".format(self.tag_name)

        subscriber = self.context.get('subscriber')
        newsletter = self.context.get('newsletter')
        message = self.context.get('message')

        kwargs = {}
        if subscriber is not None:
            kwargs['subscriber_guid'] = subscriber.guid
        if newsletter is not None:
            kwargs['newsletter_guid'] = newsletter.guid
        if message is not None:
            kwargs['message_guid'] = message.guid

        return full_reverse('unsubscription', kwargs=kwargs)

register.tag('unsubscription_url', UnsubscriptionUrlTag.as_tag())
