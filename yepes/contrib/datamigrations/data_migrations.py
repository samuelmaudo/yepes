# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import collections

from django.db import models
from django.utils import six
from django.utils.six.moves import zip

from yepes.contrib.datamigrations.fields import (
    BooleanField,
    DateField, DateTimeField, TimeField,
    FileField,
    FloatField, IntegerField, NumberField,
    TextField,
)
from yepes.contrib.datamigrations.importation_plans import importation_plans
from yepes.contrib.datamigrations.serializers import serializers
from yepes.types import Undefined
from yepes.utils.properties import cached_property


class DataMigration(object):

    can_create = False
    can_update = False

    fields = []

    def export_data(self, file=None, serializer=None):
        serializer = self.get_serializer(serializer)
        headers = [fld.name for fld in self.fields_to_export]
        data = self.get_data_to_export(serializer)
        return serializer.serialize(headers, data, file)

    def get_data_to_export(self, serializer):
        raise NotImplementedError('Subclasses of DataMigration must override get_data_to_export() method')

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

    def get_importation_plan(self, plan_class):
        if isinstance(plan_class, six.string_types):
            plan_class = importation_plans.get_plan(plan_class)

        return plan_class(self)

    def get_serializer(self, serializer=None):
        if serializer is None:
            serializer = 'json'

        if isinstance(serializer, six.string_types):
            serializer = serializers.get_serializer(serializer)

        if isinstance(serializer, collections.Callable):
            serializer = serializer()

        return serializer

    def import_data(self, source, serializer=None, plan=None, batch_size=100):
        serializer = self.get_serializer(serializer)
        data = self.get_data_to_import(source, serializer)
        plan = self.get_importation_plan(plan)
        plan.run(data, batch_size)

    @property
    def fields_to_export(self):
        return self.fields

    @property
    def fields_to_import(self):
        return self.fields


class BaseModelMigration(DataMigration):

    def __init__(self, model, use_base_manager=False,
                       ignore_missing_foreign_keys=False):

        self.model = model
        self.use_base_manager = use_base_manager
        self.ignore_missing_foreign_keys = ignore_missing_foreign_keys

    def get_data_to_export(self, serializer):
        if self.use_base_manager:
            manager = self.model._base_manager
        else:
            manager = self.model._default_manager

        qs = manager.get_queryset()
        if self.requires_model_instances:
            return self._data_from_objects(qs, serializer)
        else:
            return self._data_from_values(qs, serializer)

    def _data_from_objects(self, queryset, serializer):
        fields =  self.fields_to_export
        if (queryset._result_cache is None
                and not queryset._prefetch_related_lookups):
            queryset = queryset.iterator()

        return (
            [
                fld.export_value(
                    fld.value_from_object(obj),
                    serializer,
                )
                for fld
                in fields
            ]
            for obj
            in queryset
        )

    def _data_from_values(self, queryset, serializer):
        fields =  self.fields_to_export
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

    def get_importation_plan(self, plan_class=None):
        if plan_class is None:
            plan_class = 'update_or_create' if self.can_update else 'create'

        return super(BaseModelMigration, self).get_importation_plan(plan_class)

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
            in self.model._meta.get_fields()
            if not (f.is_relation and f.auto_created)
                and not f.blank
                and not f.has_default()
        }
        return (required_fields <= included_fields)

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
                        and f1.remote_field is not None and f2.remote_field is None):
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
                        in opts.get_fields()
                        if not (f.is_relation and f.auto_created)
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
                if f.remote_field is None:
                    break  # If no relation, next steps cannot be model fields.

                model = f.remote_field.model

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


class ModelMigration(BaseModelMigration):

    def __init__(self, model, fields=None, exclude=None,
                       use_natural_primary_keys=False,
                       use_natural_foreign_keys=False,
                       use_base_manager=False,
                       ignore_missing_foreign_keys=False):

        super(ModelMigration, self).__init__(model, use_base_manager,
                                            ignore_missing_foreign_keys)
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
            self.excluded_fields = {
                name if name != 'pk' else model._meta.pk.name
                for name
                in exclude
            }
        self.use_natural_primary_keys = use_natural_primary_keys
        self.use_natural_foreign_keys = use_natural_foreign_keys

    def build_field(self, model_field, path=None, name=None, attname=None):
        if hasattr(model_field, 'migrationfield'):
            return model_field.migrationfield(path, name, attname)

        if path is None:
            path = model_field.attname
        if name is None:
            name = model_field.name
        if attname is None:
            attname = path

        if isinstance(model_field, (models.BooleanField, models.NullBooleanField)):
            field_class = BooleanField
        elif isinstance(model_field, models.DateTimeField):
            field_class = DateTimeField
        elif isinstance(model_field, models.DateField):
            field_class = DateField
        elif isinstance(model_field, models.FileField):
            field_class = FileField
        elif isinstance(model_field, models.FloatField):
            field_class = FloatField
        elif isinstance(model_field, (models.IntegerField, models.AutoField)):
            field_class = IntegerField
        elif isinstance(model_field, models.DecimalField):
            field_class = NumberField
        elif isinstance(model_field, (models.CharField, models.TextField,
                                      models.FilePathField,
                                      models.IPAddressField, models.GenericIPAddressField)):
            field_class = TextField
        elif isinstance(model_field, models.TimeField):
            field_class = TimeField
        else:
            return None

        return field_class(path, name, attname)

    def build_relation(self, model_field):
        # Discard ManyToManyFields and GenericForeignKeys
        if not isinstance(model_field, models.ForeignKey):
            return None

        path = model_field.attname
        name = model_field.name
        attname = path

        target_field = model_field.target_field

        if self.use_natural_foreign_keys:
            opts = target_field.model._meta
            natural_key = self.find_natural_key(
                               opts.get_fields(),
                               opts.unique_together)

            if natural_key is not None:
                if not isinstance(natural_key, collections.Iterable):

                    fld = self.build_field(
                               natural_key,
                               ''.join((name, '__', natural_key.attname)),
                               ''.join((name, '__', natural_key.name)),
                               attname)

                    if fld is not None:
                        return [(fld, [model_field, natural_key])]

                else:

                    flds = [
                        self.build_field(
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

        fld = self.build_field(target_field, path, name, attname)
        return [(fld, [model_field])]

    def find_natural_key(self, model_fields, unique_together=()):
        for f in model_fields:
            if not f.is_relation and f.unique and not f.primary_key:
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
        model_fields = [
            f
            for f
            in opts.get_fields()
            if not (f.is_relation and f.auto_created)
        ]
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
            if f.is_relation:
                rel = self.build_relation(f)
                if rel is not None:
                    fields.extend(rel)
            else:
                fld = self.build_field(f)
                if fld is not None:
                    fields.append((fld, [f]))

        return collections.OrderedDict(fields)


class QuerySetExportation(ModelMigration):

    can_create = False
    can_update = False

    fields_to_import = []

    def __init__(self, queryset):
        model = queryset.model
        opts = model._meta
        fields = None
        exclude = None

        field_names, defer = queryset.query.deferred_loading
        if field_names:
            field_names = sorted(field_names, key=(
                lambda n: opts.get_field(n).creation_counter))
            if defer:
                exclude = field_names
            else:
                fields = field_names

        super(QuerySetExportation, self).__init__(model, fields, exclude)
        self.queryset = queryset

    def get_data_to_export(self, serializer):
        if self.requires_model_instances:
            return self._data_from_objects(self.queryset, serializer)
        else:
            return self._data_from_values(self.queryset, serializer)

    def get_data_to_import(self, *args, **kwargs):
        raise TypeError('This migration does not support importations.')

    def get_importation_plan(self, *args, **kwargs):
        raise TypeError('This migration does not support importations.')

    def import_data(self, *args, **kwargs):
        raise TypeError('This migration does not support importations.')

    @cached_property
    def requires_model_instances(self):
        return (self.queryset._result_cache is not None
                or self.queryset._prefetch_related_lookups)

