# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import timezone

from yepes.loading import get_model


def message_bounced(sender, instance, created, **kwargs):
    if created:
        Delivery = get_model('newsletters', 'Delivery')
        Delivery._default_manager.filter(
            message=instance.message_id,
            subscriber=instance.subscriber_id,
            is_bounced=False,
        ).update(is_bounced=True, bounce_date=timezone.now())


def message_clicked(sender, instance, created, **kwargs):
    if created:
        Delivery = get_model('newsletters', 'Delivery')
        now = timezone.now()
        Delivery._default_manager.filter(
            message=instance.message_id,
            subscriber=instance.subscriber_id,
            is_clicked=False,
        ).update(is_clicked=True, click_date=now)
        Delivery._default_manager.filter(         # Subscribers
            message=instance.message_id,          # cannot click
            subscriber=instance.subscriber_id,    # on links without
            is_opened=False ,                     # first opening
        ).update(is_opened=True, open_date=now)   # the message.


def message_opened(instance, created, **kwargs):
    if created:
        Delivery = get_model('newsletters', 'Delivery')
        Delivery._default_manager.filter(
            message=instance.message_id,
            subscriber=instance.subscriber_id,
            is_opened=False,
        ).update(is_opened=True, open_date=timezone.now())

