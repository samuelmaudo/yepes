# -*- coding:utf-8 -*-

from django.db.models.signals import post_save

from yepes.contrib.newsletters import receivers
from yepes.contrib.newsletters.abstract_models import (
    AbstractBounce,
    AbstractClick,
    AbstractDelivery,
    AbstractDomain,
    AbstractMessage,
    AbstractMessageImage,
    AbstractMessageLink,
    AbstractNewsletter,
    AbstractOpen,
    AbstractSubscriber,
    AbstractSubscriberTag,
    AbstractSubscription,
    AbstractUnsubscription,
    AbstractUnsubscriptionReason,
)

class Bounce(AbstractBounce):
    pass

class Click(AbstractClick):
    pass

class Delivery(AbstractDelivery):
    pass

class Domain(AbstractDomain):
    pass

class Message(AbstractMessage):
    pass

class MessageImage(AbstractMessageImage):
    pass

class MessageLink(AbstractMessageLink):
    pass

class Newsletter(AbstractNewsletter):
    pass

class Open(AbstractOpen):
    pass

class Subscriber(AbstractSubscriber):
    pass

class SubscriberTag(AbstractSubscriberTag):
    pass

class Subscription(AbstractSubscription):
    pass

class Unsubscription(AbstractUnsubscription):
    pass

class UnsubscriptionReason(AbstractUnsubscriptionReason):
    pass


post_save.connect(receivers.message_bounced, sender=Bounce)
post_save.connect(receivers.message_clicked, sender=Click)
post_save.connect(receivers.message_opened, sender=Open)

