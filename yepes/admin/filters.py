# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.admin import FieldListFilter
from django.contrib.admin.util import get_model_from_relation
from django.db.models import F, Q
from django.db.models.related import RelatedObject
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _

from yepes.model_mixins import Nestable


class NestableFieldListFilter(FieldListFilter):

    level_indicator = '– '

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '{0}__in'.format(field_path)
        self.lookup_kwarg_isnull = '{0}__isnull'.format(field_path)
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        self.lookup_val_isnull = request.GET.get(self.lookup_kwarg_isnull)
        self.other_model = get_model_from_relation(field)
        opts = self.other_model._mptt_meta
        qs = self.other_model._default_manager
        if self.other_model is model:
            qs = qs.filter(**{
                '{0}__gt'.format(opts.right_attr): F(opts.left_attr) + 1,
            })
        self.objects = qs.order_by(opts.tree_id_attr, opts.left_attr)
        super(NestableFieldListFilter, self).__init__(field, request, params, model, model_admin, field_path)

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None and not self.lookup_val_isnull,
            'query_string': cl.get_query_string({},
                [self.lookup_kwarg, self.lookup_kwarg_isnull]),
            'display': _('All'),
        }
        if ((isinstance(self.field, RelatedObject) and self.field.field.null)
                    or (hasattr(self.field, 'rel') and self.field.null)):
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': cl.get_query_string({
                    self.lookup_kwarg_isnull: 'True',
                }, [self.lookup_kwarg]),
                'display': _('None'),
            }
        for obj in self.objects:
            yield {
                'selected': self.lookup_val == smart_text(obj._get_pk_val()),
                'query_string': cl.get_query_string({
                    self.lookup_kwarg: smart_text(obj._get_pk_val()),
                }, [self.lookup_kwarg_isnull]),
                'display': self.label(obj),
            }

    def expected_parameters(self):
        return [self.lookup_kwarg, self.lookup_kwarg_isnull]

    def has_output(self):
        choices_count = len(self.objects)
        if ((isinstance(self.field, RelatedObject) and self.field.field.null)
                    or (hasattr(self.field, 'rel') and self.field.null)):
            choices_count += 1
        return choices_count > 1

    def label(self, obj):
        return '{0} {1}'.format(
                self.level_indicator * obj.get_level_number(),
                smart_text(obj))

    def queryset(self, request, queryset):
        if self.lookup_val_isnull:
            return queryset.filter(**{self.lookup_kwarg_isnull: True})
        elif self.lookup_val is not None:
            obj = self.other_model._default_manager.get(pk=self.lookup_val)
            objects = obj.get_descendants(include_self=True)
            return queryset.filter(**{self.lookup_kwarg: objects})

FieldListFilter.register(
    lambda f: (
        bool(getattr(f, 'rel', None))
            and issubclass(f.rel.to, Nestable)
        or
        isinstance(f, RelatedObject)
            and issubclass(f.field.rel.to, Nestable)
    ),
    NestableFieldListFilter,
    take_priority=True,
)

