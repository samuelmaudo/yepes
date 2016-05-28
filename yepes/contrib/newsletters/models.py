# -*- coding:utf-8 -*-

from yepes.apps import apps

AbstractBounce = apps.get_class('newsletters.abstract_models', 'AbstractBounce')
AbstractClick = apps.get_class('newsletters.abstract_models', 'AbstractClick')
AbstractDelivery = apps.get_class('newsletters.abstract_models', 'AbstractDelivery')
AbstractDomain = apps.get_class('newsletters.abstract_models', 'AbstractDomain')
AbstractMessage = apps.get_class('newsletters.abstract_models', 'AbstractMessage')
AbstractMessageImage = apps.get_class('newsletters.abstract_models', 'AbstractMessageImage')
AbstractMessageLink = apps.get_class('newsletters.abstract_models', 'AbstractMessageLink')
AbstractNewsletter = apps.get_class('newsletters.abstract_models', 'AbstractNewsletter')
AbstractOpen = apps.get_class('newsletters.abstract_models', 'AbstractOpen')
AbstractSubscriber = apps.get_class('newsletters.abstract_models', 'AbstractSubscriber')
AbstractSubscriberTag = apps.get_class('newsletters.abstract_models', 'AbstractSubscriberTag')
AbstractSubscription = apps.get_class('newsletters.abstract_models', 'AbstractSubscription')
AbstractUnsubscription = apps.get_class('newsletters.abstract_models', 'AbstractUnsubscription')
AbstractUnsubscriptionReason = apps.get_class('newsletters.abstract_models', 'AbstractUnsubscriptionReason')


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

