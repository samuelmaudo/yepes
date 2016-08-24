# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six

from yepes.contrib.datamigrations import CustomDataMigration, TextField
from yepes.loading import LazyClass, LazyModel
from yepes.utils.properties import cached_property

Subscriber = LazyModel('newsletters', 'Subscriber')
SubscriberPlan = LazyClass('newsletters.importation_plans', 'SubscriberPlan')


class SubscriberImportation(CustomDataMigration):

    fields = [
        TextField('email_address'),
        TextField('first_name'),
        TextField('last_name'),
        TextField('newsletters'),
        TextField('tags'),
    ]
    def __init__(self):
        super(SubscriberImportation, self).__init__(Subscriber, True)

    def export_data(self, *args, **kwargs):
        raise TypeError('This migration does not support exportations.')

    def get_data_to_export(self, *args, **kwargs):
        raise TypeError('This migration does not support exportations.')

    def get_importation_plan(self, plan_class=None):
        return SubscriberPlan(self)

    @property
    def can_create(self):
        return True

    @property
    def can_update(self):
        return False

    @cached_property
    def fields_to_import(self):
        return list(self.fields)

    @cached_property
    def primary_key(self):
        return next(six.itervalues(self.model_fields))[0]

