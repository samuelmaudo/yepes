# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.apps import apps
from yepes.model_mixins import Nestable, ParentForeignKey

ParameterManager = apps.get_class('metrics.managers', 'ParameterManager')


@python_2_unicode_compatible
class Parameter(Nestable):

    parent = ParentForeignKey(
            'self',
            null=True,
            on_delete=models.CASCADE,
            related_name='children',
            verbose_name=_('Parent'))
    index = fields.IntegerField(
            null=True,
            blank=True,
            min_value=0,
            verbose_name=_('Index'))
    name = fields.CharField(
            unique=True,
            max_length=63,
            verbose_name=_('Name'))
    token = fields.CharField(
            max_length=255,
            verbose_name=_('Token'),
            help_text=_('Used to check the User-Agent strings.'))
    regex = fields.BooleanField(
            default=False,
            verbose_name=_('Regular Expression'),
            help_text=_('Check this if your token is a regular expression.'))

    objects = ParameterManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains', )

    def check(self, user_agent_string):
        token = self.token.lower()
        ua = user_agent_string.lower()
        if self.regex:
            return (re.search(token, ua) is not None)
        else:
            return (token in ua)

