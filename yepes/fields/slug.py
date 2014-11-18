# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.six.moves import xrange

from yepes.utils import slugify


class SlugField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = False
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('max_length', 63)
        kwargs['null'] = False

        self.force_ascii = kwargs.pop('force_ascii', True)
        self.unique_with_respect_to = kwargs.pop('unique_with_respect_to', None)
        if self.unique_with_respect_to is not None:
            kwargs['unique'] = False

        super(SlugField, self).__init__(*args, **kwargs)
        self.base_length = self.max_length - 3

    def avoid_duplicates(self, base_slug, model_instance):
        if len(base_slug) > (self.base_length):
            base_slug = base_slug[:self.base_length].rstrip('-')

        qs = self.model._default_manager.get_queryset()
        if model_instance.pk:
            qs = qs.exclude(pk=model_instance.pk)

        if self.unique_with_respect_to is not None:
            field = self.unique_with_respect_to
            qs = qs.filter(**{
                field: getattr(model_instance, field),
            })

        for i in xrange(1, 64):
            if i == 1:
                slug = base_slug
            else:
                slug = '{0}-{1}'.format(base_slug, i)

            if not qs.filter(**{self.name: slug}).exists():
                break

        return slug

    def clean(self, value, model_instance):
        slug = self.to_python(value)
        if not slug:
            slug = self.to_slug(model_instance)
            if self.unique or self.unique_with_respect_to is not None:
                slug = self.avoid_duplicates(slug, model_instance)
        else:
            slug = self.to_slug(slug)
            if self.unique or self.unique_with_respect_to is not None:
                slug = self.avoid_duplicates(slug, model_instance)

        self.validate(slug, model_instance)
        self.run_validators(slug)
        return slug

    def formfield(self, **kwargs):
        kwargs['required'] = False
        return super(SlugField, self).formfield(**kwargs)

    def pre_save(self, model_instance, add):
        slug = super(SlugField, self).pre_save(model_instance, add)
        if not slug:
            slug = self.to_slug(model_instance)
            if self.unique or self.unique_with_respect_to is not None:
                slug = self.avoid_duplicates(slug, model_instance)

            setattr(model_instance, self.attname, slug)

        return slug

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.CharField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

    def to_slug(self, value):
        return slugify(value, ascii=self.force_ascii)

