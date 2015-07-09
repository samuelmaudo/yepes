# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.db.models import F, Q
from django.db.models.base import ModelBase
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.types import Undefined

__all__ = ('Orderable', 'OrderableBase')


class OrderableBase(ModelBase):
    """
    Checks for ``order_with_respect_to`` on the model's inner ``Meta`` class
    and if found, copies it to `filter_field` and deletes it since it will
    cause errors when used with ``ForeignKey('self')``.

    Also creates the ``ordering`` attribute on the ``Meta`` class if not yet
    provided.

    """
    def __new__(cls, name, bases, attrs):
        # six.with_metaclass() inserts an extra class called 'NewBase' in the
        # inheritance tree: Model -> NewBase -> object. But the initialization
        # should be executed only once for a given model class.

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == 'NewBase' and attrs == {}:
            return super(ModelBase, cls).__new__(cls, name, bases, attrs)

        if 'Meta' in attrs:
            if hasattr(attrs['Meta'], 'order_with_respect_to'):
                filter_field = attrs['Meta'].order_with_respect_to
                delattr(attrs['Meta'], 'order_with_respect_to')
            else:
                filter_field = None
        else:
            for base in bases:
                if hasattr(base, '_meta'):
                    filter_field = getattr(base._meta, 'filter_field', None)
                    break
            else:
                filter_field = None

        new_cls = super(OrderableBase, cls).__new__(cls, name, bases, attrs)

        opts = new_cls._meta
        opts.filter_field = filter_field
        if not opts.abstract and not opts.proxy:

            if not opts.ordering:
                if filter_field is not None:
                    opts.ordering = [filter_field, 'index']
                else:
                    opts.ordering = ['index']

            sort_field = opts.get_field('index')
            if filter_field is not None:
                if (filter_field, 'index') not in opts.index_together:
                    opts.index_together.append((filter_field, 'index'))

                sort_field.db_index = False
            else:
                sort_field.db_index = True

        return new_cls


class Orderable(six.with_metaclass(OrderableBase, models.Model)):
    """
    Abstract model that provides a custom ordering integer field similar to
    using Meta's ``order_with_respect_to``, since to date (Django 1.2) this
    doesn't work with ``ForeignKey('self')``.

    We may also want this feature for models that aren't ordered with respect
    to a particular field.

    """
    # Do not set ``db_index`` here because ``order_with_respect_to``.
    index = fields.IntegerField(
            blank=True,
            min_value=0,
            verbose_name=_('Index'))

    class Meta:
        abstract = True

    _next = Undefined
    _previous = Undefined

    def get_queryset(self):
        """
        Returns a dict to use as a filter for ordering operations containing
        the original `Meta.order_with_respect_to` value if provided.
        """
        qs = self._default_manager.get_queryset()
        if self._meta.filter_field:
            name = self._meta.filter_field
            value = getattr(self, name)
            return qs.filter(**{name: value})
        else:
            return qs

    def delete(self, *args, **kwargs):
        """
        Update the ordering values for siblings.
        """
        if self.index is not None:
            qs = self.get_queryset().filter(index__gt=self.index)
            qs.update(index=F('index') - 1)

        super(Orderable, self).delete(*args, **kwargs)

    def get_next_in_order(self):
        if self._next is Undefined:
            qs = self.get_queryset()
            qs = qs.filter(index__gt=self.index)
            qs = qs.order_by('index')
            self._next = qs.first()

        return self._next

    def get_previous_in_order(self):
        if self._previous is Undefined:
            qs = self.get_queryset()
            qs = qs.filter(index__lt=self.index)
            qs = qs.order_by('index')
            self._previous = qs.last()

        return self._previous

    def save(self, **kwargs):
        """
        Set the initial ordering value.
        """
        updated_fields = kwargs.get('update_fields', ())
        new_record = (kwargs.get('force_insert', False)
                      or not (self.pk or updated_fields))

        self._next = Undefined
        self._previous = Undefined
        if new_record and not self.index:
            qs = self.get_queryset()
            self.index = qs.filter(index__isnull=False).count()

        super(Orderable, self).save(**kwargs)

