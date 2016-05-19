# -*- coding:utf-8 -*-

import inspect

from django.db import models

from yepes.types import Undefined
from yepes.utils.properties import cached_property


class Calculated(models.Model):

    class Meta:
        abstract = True

    _calculated_fields = Undefined
    _cached_properties = Undefined

    def clear_calculated_values(self):
        for field in self.get_calculated_fields():
            self.__dict__.pop(field, None)
        for property in self.get_cached_properties():
            self.__dict__.pop(property, None)

    @classmethod
    def get_calculated_fields(cls):
        if cls._calculated_fields is Undefined:
            cls._calculated_fields = tuple(
                field.attname
                for field
                in cls._meta.get_fields()
                if getattr(field, 'calculated', False)
            )
        return cls._calculated_fields

    @classmethod
    def get_cached_properties(cls):
        if cls._cached_properties is Undefined:
            cls._cached_properties = tuple(
                name
                for name, value
                in inspect.getmembers(cls)
                if isinstance(value, cached_property)
            )
        return cls._cached_properties

    def save(self, **kwargs):
        self.clear_calculated_values()
        super(Calculated, self).save(**kwargs)

    def save_calculated_fields(self):
        if not self._get_pk_val():
            # This avoids partial storages when the record
            # has not been stored yet.
            self.save()
        else:
            self.save(update_fields=self.get_calculated_fields())

