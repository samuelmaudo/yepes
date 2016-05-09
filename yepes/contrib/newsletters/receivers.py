# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import timezone

from yepes.loading import LazyModel

Delivery = LazyModel('newsletters', 'Delivery')


def message_bounced(sender, instance, created, **kwargs):
    if created:
        Delivery.objects.filter(
            message=instance.message_id,
            subscriber=instance.subscriber_id,
            is_bounced=False,
        ).update(is_bounced=True, bounce_date=timezone.now())


def message_clicked(sender, instance, created, **kwargs):
    if created:
        now = timezone.now()
        Delivery.objects.filter(
            message=instance.message_id,
            subscriber=instance.subscriber_id,
            is_clicked=False,
        ).update(is_clicked=True, click_date=now)
        Delivery.objects.filter(         # Subscribers
            message=instance.message_id,          # cannot click
            subscriber=instance.subscriber_id,    # on links without
            is_opened=False ,                     # first opening
        ).update(is_opened=True, open_date=now)   # the message.


def message_opened(instance, created, **kwargs):
    if created:
        Delivery.objects.filter(
            message=instance.message_id,
            subscriber=instance.subscriber_id,
            is_opened=False,
        ).update(is_opened=True, open_date=timezone.now())

