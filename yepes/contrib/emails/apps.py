# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from yepes.apps import OverridableConfig


class EmailsConfig(OverridableConfig):
    name = 'yepes.contrib.emails'
    verbose_name = _('Emails')

