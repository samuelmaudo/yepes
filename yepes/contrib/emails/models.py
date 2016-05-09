# -*- coding:utf-8 -*-

from yepes.apps import apps

AbstractConnection = apps.get_class('emails.abstract_models', 'AbstractConnection')
AbstractDelivery = apps.get_class('emails.abstract_models', 'AbstractDelivery')
AbstractMessage = apps.get_class('emails.abstract_models', 'AbstractMessage')


class Connection(AbstractConnection):
    pass

class Delivery(AbstractDelivery):
    pass

class Message(AbstractMessage):
    pass

