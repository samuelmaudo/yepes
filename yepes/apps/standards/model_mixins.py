# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import re

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import six
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.conf import settings
from yepes.exceptions import MissingAttributeError

NAME_RE = re.compile(r'^name_[a-z]{2}$')


class LocalizedNameField(fields.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('blank', True)
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('max_length', 127)
        super(LocalizedNameField, self).__init__(*args, **kwargs)

    def get_attname(self):
        return ''.join(('_', self.name))

    def get_attname_column(self):
        attname = self.get_attname()
        column = self.db_column or self.name
        return attname, column


@python_2_unicode_compatible
class Standard(models.Model):

    name = fields.CharField(
            unique=True,
            max_length=127,
            verbose_name=_('Native Name'))
    name_de = LocalizedNameField(
            verbose_name=_('German Name'))
    name_en = LocalizedNameField(
            verbose_name=_('English Name'))
    name_es = LocalizedNameField(
            verbose_name=_('Spanish Name'))
    name_fr = LocalizedNameField(
            verbose_name=_('French Name'))
    name_pt = LocalizedNameField(
            verbose_name=_('Portuguese Name'))
    name_ru = LocalizedNameField(
            verbose_name=_('Russian Name'))
    name_zh = LocalizedNameField(
            verbose_name=_('Chinese Name'))

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        for attr_name in six.iterkeys(kwargs):
            if NAME_RE.search(attr_name) is not None:
                attr_value = kwargs.pop(attr_name)
                kwargs[''.join(('_', attr_name))] = attr_value

        super(Standard, self).__init__(*args, **kwargs)

    def __getattr__(self, attr_name):
        if NAME_RE.search(attr_name) is None:
            raise MissingAttributeError(self, attr_name)

        name = self.__dict__.get(''.join(('_', attr_name)))
        if name:
            return name

        fallback = settings.STANDARDS_FALLBACK_TRANSLATION
        if fallback != 'native':
            name = self.__dict__.get(''.join(('_name_', fallback)))
            if name:
                return name

        return self.name

    def __setattr__(self, attr_name, attr_value):
        if (attr_name.startswith('_')
                or NAME_RE.search(attr_name) is None):
            super(Standard, self).__setattr__(attr_name, attr_value)
        else:
            self.__dict__[''.join(('_', attr_name))] = attr_value

    def __str__(self):
        if settings.STANDARDS_DEFAULT_TRANSLATION == 'native':
            return self.name

        if settings.STANDARDS_DEFAULT_TRANSLATION == 'locale':
            language = translation.get_language()
        else:
            language = settings.STANDARDS_DEFAULT_TRANSLATION

        return getattr(self, ''.join(('name_', language[:2])))

