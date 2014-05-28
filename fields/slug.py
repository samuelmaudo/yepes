# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.six.moves import xrange

from yepes.utils import slugify


class SlugField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('max_length', 63)
        kwargs['null'] = False
        kwargs.setdefault('unique', True)
        self.force_ascii = kwargs.pop('force_ascii', True)
        super(SlugField, self).__init__(*args, **kwargs)
        self.base_length = self.max_length - 3

    def avoid_duplicates(self, base_slug, model_instance):
        manager = self.model._default_manager
        if len(base_slug) > (self.base_length):
            base_slug = base_slug[:self.base_length].rstrip('-')

        for i in xrange(63):
            if not model_instance.pk:
                qs = manager.all()
            else:
                qs = manager.exclude(pk=model_instance.pk)

            if i == 0:
                slug = base_slug
            else:
                slug = '{0}-{1}'.format(base_slug, i)

            if not qs.filter(**{self.name: slug}).exists():
                break

        setattr(model_instance, self.attname, slug)
        return slug

    def clean(self, value, model_instance):
        slug = self.to_python(value)
        if not slug:
            slug = self.to_slug(model_instance)
            if self.unique:
                slug = self.avoid_duplicates(slug, model_instance)
        else:
            slug = self.to_slug(slug)
            manager = self.model._default_manager
            if (self.unique
                    and (not model_instance.pk
                            or slug != manager.filter(pk=model_instance.pk) \
                                              .values_list(self.name, flat=True) \
                                              .first())):
                slug = self.avoid_duplicates(slug, model_instance)

        self.validate(slug, model_instance)
        self.run_validators(slug)
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

