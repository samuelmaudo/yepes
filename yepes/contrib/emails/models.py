# -*- coding:utf-8 -*-

from yepes.contrib.emails.abstract_models import (
    AbstractConnection,
    AbstractDelivery,
    AbstractMessage,
)

class Connection(AbstractConnection):
    pass

class Delivery(AbstractDelivery):
    pass

class Message(AbstractMessage):
    pass
