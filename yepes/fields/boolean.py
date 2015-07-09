# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models

from yepes.fields.calculated import CalculatedField


class BooleanField(CalculatedField, models.BooleanField):

    def deconstruct(self):
        name, path, args, kwargs = super(BooleanField, self).deconstruct()
        path = path.replace('yepes.fields.boolean', 'yepes.fields')
        return (name, path, args, kwargs)


class NullBooleanField(CalculatedField, models.NullBooleanField):

    def deconstruct(self):
        name, path, args, kwargs = super(NullBooleanField, self).deconstruct()
        path = path.replace('yepes.fields.boolean', 'yepes.fields')
        return (name, path, args, kwargs)

