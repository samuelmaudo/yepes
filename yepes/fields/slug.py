# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils.six.moves import range
from django.utils.translation import ugettext_lazy as _

from yepes import forms
from yepes.fields.char import CharField
from yepes.utils import slugify
from yepes.utils.deconstruct import clean_keywords


class SlugField(CharField):

    description = _('Slug')

    def __init__(self, *args, **kwargs):
        kwargs['blank'] = False
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('force_ascii', True)
        kwargs.setdefault('max_length', 63)
        kwargs['normalize_spaces'] = False
        kwargs['null'] = False
        kwargs['trim_spaces'] = False

        self.unique_with_respect_to = kwargs.pop('unique_with_respect_to', None)
        if self.unique_with_respect_to is not None:
            kwargs['unique'] = False

        super(SlugField, self).__init__(*args, **kwargs)
        self.base_length = self.max_length - 3

    def avoid_duplicates(self, base_slug, model_instance):
        model_instance_id = model_instance._get_pk_val()

        if len(base_slug) > (self.base_length):
            base_slug = base_slug[:self.base_length].rstrip('-')

        qs = self.model._default_manager.get_queryset()
        if model_instance_id:
            qs = qs.exclude(pk=model_instance_id)

        if self.unique_with_respect_to is not None:
            field = self.unique_with_respect_to
            qs = qs.filter(**{
                field: getattr(model_instance, field),
            })

        for i in range(1, 64):
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
            slug = self.to_python(model_instance)

        if self.unique or self.unique_with_respect_to is not None:
            slug = self.avoid_duplicates(slug, model_instance)

        self.validate(slug, model_instance)
        self.run_validators(slug)
        return slug

    def deconstruct(self):
        name, path, args, kwargs = super(SlugField, self).deconstruct()
        path = path.replace('yepes.fields.slug', 'yepes.fields')
        clean_keywords(self, kwargs, variables={
            'db_index': True,
            'force_ascii': True,
            'max_length': 63,
            'unique_with_respect_to': None,
        }, constants=[
            'blank',
            'normalize_spaces',
            'null',
            'trim_spaces',
        ])
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', forms.SlugField)
        kwargs.setdefault('required', False)
        return super(SlugField, self).formfield(**kwargs)

    def pre_save(self, model_instance, add):
        slug = super(SlugField, self).pre_save(model_instance, add)
        if not slug:
            slug = self.to_python(model_instance)
            if self.unique or self.unique_with_respect_to is not None:
                slug = self.avoid_duplicates(slug, model_instance)

            setattr(model_instance, self.attname, slug)

        return slug

    def to_python(self, *args, **kwargs):
        value = super(SlugField, self).to_python(*args, **kwargs)
        if value:
            return slugify(value)
        else:
            return value

