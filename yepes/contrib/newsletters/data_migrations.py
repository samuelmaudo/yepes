# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import six

from yepes.contrib.datamigrations import BaseModelMigration, TextField
from yepes.loading import LazyClass, LazyModel
from yepes.utils.properties import cached_property

Subscriber = LazyModel('newsletters', 'Subscriber')
SubscriberPlan = LazyClass('newsletters.importation_plans', 'SubscriberPlan')


class SubscriberImportation(BaseModelMigration):

    can_create = True
    can_export = False
    can_update = False

    fields = [
        TextField('email_address'),
        TextField('first_name'),
        TextField('last_name'),
        TextField('newsletters'),
        TextField('tags'),
    ]

    def __init__(self):
        super(SubscriberImportation, self).__init__(Subscriber)

    def get_importation_plan(self, *args, **kwargs):
        return SubscriberPlan(self)

    @property
    def fields_to_import(self):
        return self.fields

    @cached_property
    def primary_key(self):
        return next(six.itervalues(self.model_fields))[0]

