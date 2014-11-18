# -*- coding:utf-8 -*-

from __future__ import unicode_literals


class ConfigDoesNotExist(ValueError):

    def __init__(self, key):
        msg = "No Configuration found matching '{0}'"
        super(ConfigDoesNotExist, self).__init__(msg.format(key))
        self.key = key

