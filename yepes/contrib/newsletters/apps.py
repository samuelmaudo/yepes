# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from yepes.apps import OverridableConfig


class NewslettersConfig(OverridableConfig):

    name = 'yepes.contrib.newsletters'
    verbose_name = _('Newsletters')

    def ready(self):
        super(NewslettersConfig, self).ready()
        message_bounced = self.get_class('receivers', 'message_bounced')
        message_clicked = self.get_class('receivers', 'message_clicked')
        message_opened = self.get_class('receivers', 'message_opened')
        post_save.connect(message_bounced, self.get_model('Bounce'))
        post_save.connect(message_clicked, self.get_model('Click'))
        post_save.connect(message_opened, self.get_model('Open'))

