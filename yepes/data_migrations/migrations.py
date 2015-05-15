# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections

from django.db import models
from django.db import transaction
from django.utils import six
from django.utils.six.moves import zip

from yepes.data_migrations import fields
from yepes.data_migrations import importation_plans
from yepes.data_migrations import serializers
from yepes.data_migrations.importation_plans.create import CreatePlan
from yepes.data_migrations.importation_plans.update_or_create import UpdateOrCreatePlan
from yepes.data_migrations.serializers.json import JsonSerializer
from yepes.types import Undefined
from yepes.utils.iterators import isplit
from yepes.utils.properties import cached_property


class CustomDataMigration(object):

    fields = []

    def __init__(self, model):
        self.model = model

    def export_data(self, file=None, serializer=None):
        serializer = self.get_serializer(serializer)
        headers = [fld.name for fld in self.fields]
        data = self.get_data_to_export(serializer)
        return serializer.serialize(headers, data, file)

    def get_data_to_export(self, serializer):
        qs = self.model._default_manager.all()
        if self.requires_model_instances:
            return self._get_data_from_objects(qs, serializer)
        else:
            return self._get_data_from_values(qs, serializer)

    def _get_data_from_objects(self, queryset, serializer):
        fields =  self.fields
        if (queryset._result_cache is None
                and not queryset._prefetch_related_lookups):
            queryset = queryset.iterator()

        return (
            [
                fld.export_value(
                    fld.get_value_from_object(obj),
                    serializer,
                )
                for fld
                in fields
            ]
            for obj
            in queryset
        )

    def _get_data_from_values(self, queryset, serializer):
        fields =  self.fields
        return (
            [
                fld.export_value(val, serializer)
                for val, fld
                in zip(row, fields)
            ]
            for row
            in queryset.values_list(*[
                fld.path
                for fld
                in fields
            ]).iterator()
        )

    def get_data_to_import(self, source, serializer):
        fields = self.fields_to_import
        headers = [fld.name for fld in fields]
        data = serializer.deserialize(headers, source)
        return (
            {
                fld.path: fld.import_value(val, serializer)
                for val, fld
                in zip(row, fields)
                if val is not Undefined
            }
            for row
            in data
        )

    def get_importation_plan(self, data, plan_class=None):
        if plan_class is None:
            plan_class = UpdateOrCreatePlan if self.can_update else CreatePlan
        elif isinstance(plan_class, six.string_types):
            plan_class = importation_plans.get_plan(plan_class)

        return plan_class(self)

    def get_serializer(self, serializer=None):
        if serializer is None:
            serializer = JsonSerializer()
        elif isinstance(serializer, six.string_types):
            serializer = serializers.get_serializer(serializer)()
        elif isinstance(serializer, collections.Callable):
            serializer = serializer()

        return serializer

    def import_data(self, source, serializer=None, plan=None, batch_size=100):
        serializer = self.get_serializer(serializer)
        data = self.get_data_to_import(source, serializer)
        plan = self.get_importation_plan(data, plan)
        plan.check()
        with transaction.atomic():
            for batch in isplit(data, batch_size):
                plan.run(plan.prepare(batch))

    @cached_property
    def can_create(self):
        included_fields = {
            self.model_fields[fld][0]
            for fld
            in self.fields_to_import
        }
        required_fields = {
            f
            for f
            in self.model._meta.fields
            if not f.blank and not f.has_default()
        }
        return (included_fields >= required_fields)

    @property
    def can_update(self):
        return (self.primary_key is not None)

    @cached_property
    def fields_to_import(self):
        fields = []
        for fld, model_fields in six.iteritems(self.model_fields):
            if (len(model_fields) == 1
                    and '__' not in fld.path):
                fields.append(fld)
            elif (len(model_fields) == 2
                    and fld.path.count('__') == 1):
                f1, f2 = model_fields
                if (f2.unique and not f2.null
                        and f1.rel is not None and f2.rel is None):
                    fields.append(fld)  # This allows use of natural keys.

        return fields

    @cached_property
    def model_fields(self):
        models = {}
        def get_model_field(model, field_name):
            opts = model._meta
            if field_name == 'pk':
                return opts.pk
            else:
                if opts.model_name not in models:
                    models[opts.model_name] = {
                        f.name: f
                        for f
                        in opts.fields
                    }
                return models[opts.model_name].get(field_name)

        fields = []
        field_paths = [
            (fld, fld.path.split('__'))
            for fld
            in self.fields
        ]
        for fld, path in field_paths:
            model = self.model
            model_fields = []
            for step in path:
                f = get_model_field(model, step)
                if f is None:
                    break  # This step is probably an object property.

                model_fields.append(f)
                if f.rel is None:
                    break  # If no relation, next steps cannot be model fields.

                model = f.rel.to

            fields.append((fld, model_fields))

        return collections.OrderedDict(fields)

    @cached_property
    def natural_foreign_keys(self):
        return [
            fld
            for fld
            in self.fields_to_import
            if '__' in fld.path
        ] or None

    @cached_property
    def primary_key(self):
        key = None
        opts = self.model._meta
        for fld in self.fields_to_import:
            f = self.model_fields[fld][0]
            if f.primary_key:
                return fld

            if key is None and f.unique and not f.null:
                key = fld

        if key is None and opts.unique_together:
            available_model_fields = {
                model_fields[0].name: fld
                for fld, model_fields
                in six.iteritems(self.model_fields)
                if fld in self.fields_to_import
            }
            for set in opts.unique_together:
                try:
                    key = tuple(
                        available_model_fields[name]
                        for name
                        in set
                    )
                except KeyError:
                    continue
                else:
                    break

        return key

    @cached_property
    def requires_model_instances(self):
        for fld, model_fields in six.iteritems(self.model_fields):
            if len(model_fields) < (fld.path.count('__') + 1):
                return True  # Field path points to an object property.

        return False


class DataMigration(CustomDataMigration):

    def __init__(self, model, fields=None, exclude=None,
                       use_natural_primary_keys=False,
                       use_natural_foreign_keys=False):
        super(DataMigration, self).__init__(model)
        if not fields:
            self.selected_fields = None
        else:
            self.selected_fields = [    # Field order matters
                name if name != 'pk' else model._meta.pk.name
                for name
                in fields
            ]
        if not exclude:
            self.excluded_fields = None
        else:
            self.excluded_fields = set(
                name if name != 'pk' else model._meta.pk.name
                for name
                in exclude
            )
        self.use_natural_primary_keys = use_natural_primary_keys
        self.use_natural_foreign_keys = use_natural_foreign_keys

    def construct_field(self, model_field, path=None, name=None, attname=None):
        if hasattr(model_field, 'migrationfield'):
            return model_field.migrationfield(path, name, attname)

        if path is None:
            path = model_field.attname
        if name is None:
            name = model_field.name
        if attname is None:
            attname = path

        if isinstance(model_field, (models.BooleanField, models.NullBooleanField)):
            field_class = fields.BooleanField
        elif isinstance(model_field, models.DateTimeField):
            field_class = fields.DateTimeField
        elif isinstance(model_field, models.DateField):
            field_class = fields.DateField
        elif isinstance(model_field, models.FloatField):
            field_class = fields.FloatField
        elif isinstance(model_field, (models.IntegerField, models.AutoField)):
            field_class = fields.IntegerField
        elif isinstance(model_field, models.DecimalField):
            field_class = fields.NumberField
        elif isinstance(model_field, (models.CharField, models.TextField,
                                      models.FilePathField,
                                      models.IPAddressField, models.GenericIPAddressField)):
            field_class = fields.TextField
        elif isinstance(model_field, models.TimeField):
            field_class = fields.TimeField
        else:
            return None

        return field_class(path, name, attname)

    def construct_relation(self, model_field):
        if not isinstance(model_field, models.ForeignKey):
            return None

        path = model_field.attname
        name = model_field.name
        attname = path

        related_field = model_field.related_field

        if self.use_natural_foreign_keys:
            opts = related_field.model._meta
            natural_key = self.find_natural_key(
                               opts.fields,
                               opts.unique_together)

            if natural_key is not None:
                if not isinstance(natural_key, collections.Iterable):

                    fld = self.construct_field(
                               natural_key,
                               ''.join((name, '__', natural_key.attname)),
                               ''.join((name, '__', natural_key.name)),
                               attname)

                    if fld is not None:
                        return [(fld, [model_field, natural_key])]

                else:

                    flds = [
                        self.construct_field(
                             key,
                             ''.join((name, '__', key.attname)),
                             ''.join((name, '__', key.name)),
                             attname)
                        for key
                        in natural_key
                    ]
                    if all(fld is not None for fld in flds):
                        return [
                            (fld, [model_field, key])
                            for fld, key
                            in zip(flds, natural_key)
                        ]

        fld = self.construct_field(related_field, path, name, attname)
        return [(fld, [model_field])]

    def find_natural_key(self, model_fields, unique_together=()):
        for f in model_fields:
            if f.unique and not f.primary_key:
                return f

        if unique_together:
            available_model_fields = {
                f.name: f
                for f
                in model_fields
            }
            for set in unique_together:
                try:
                    return tuple(
                        available_model_fields[name]
                        for name
                        in set
                    )
                except KeyError:
                    continue

        return None

    @cached_property
    def fields(self):
        return [fld for fld in self.model_fields]

    @cached_property
    def model_fields(self):
        opts = self.model._meta
        model_fields = opts.fields

        if self.selected_fields is not None:
            available_model_fields = {
                f.name: f
                for f
                in model_fields
            }
            model_fields = [
                available_model_fields[name]
                for name
                in self.selected_fields
            ]

        if self.excluded_fields is not None:
            model_fields = [
                f
                for f
                in model_fields
                if f.name not in self.excluded_fields
            ]

        if self.use_natural_primary_keys and self.selected_fields is None:
            key = self.find_natural_key(model_fields, opts.unique_together)
            if key is not None:
                model_fields = [
                    f
                    for f
                    in model_fields
                    if not f.primary_key
                ]

        fields = []
        for f in model_fields:
            if f.rel is None:
                fld = self.construct_field(f)
                if fld is not None:
                    fields.append((fld, [f]))
            else:
                rel = self.construct_relation(f)
                if rel is not None:
                    fields.extend(rel)

        return collections.OrderedDict(fields)


class QuerySetExportation(DataMigration):

    def __init__(self, queryset):
        field_names, defer = queryset.query.deferred_loading
        model = queryset.model
        fields = field_names if field_names and not defer else None
        exclude = field_names if field_names and defer else None
        super(QuerySetExportation, self).__init__(model, fields, exclude)
        self.queryset = queryset

    def get_data_to_export(self, serializer):
        if self.requires_model_instances:
            return self._get_data_from_objects(self.queryset, serializer)
        else:
            return self._get_data_from_values(self.queryset, serializer)

    def get_data_to_import(self, *args, **kwargs):
        raise TypeError('This migration does not support importations.')

    def get_importation_plan(self, *args, **kwargs):
        raise TypeError('This migration does not support importations.')

    def import_data(self, *args, **kwargs):
        raise TypeError('This migration does not support importations.')

    @property
    def can_create(self):
        return False

    @property
    def can_update(self):
        return False

    @property
    def fields_to_import(self):
        return []

    @cached_property
    def requires_model_instances(self):
        return (self.queryset._result_cache is not None
                or self.queryset._prefetch_related_lookups)

