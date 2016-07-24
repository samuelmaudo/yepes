# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SimpleRegistryConfig(AppConfig):

    name = 'yepes.contrib.registry'
    verbose_name = _('Registry')


class RegistryConfig(SimpleRegistryConfig):

    def ready(self):
        super(RegistryConfig, self).ready()
        self.module.autodiscover()

