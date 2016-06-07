# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import connection as conn
from django.db import transaction
from django.db.models import Manager
from django.db.models.fields import FieldDoesNotExist

from yepes.apps import apps


class SlugHistoryManager(Manager):

    statements = {
        'postgresql': {
            'populate': """

            INSERT INTO "{history}" (slug, object_type_id, object_id)
            SELECT model."{model_slug}",
                   %s,
                   model."{model_pk}"
              FROM "{model}" AS model;

            """,
            'truncate': 'TRUNCATE "{table}" RESTART IDENTITY;',
        },
        'mysql': {
            'populate': """

            INSERT INTO `{history}` (slug, object_type_id, object_id)
            SELECT model.`{model_slug}`,
                   %s,
                   model.`{model_pk}`
              FROM `{model}` AS model;

            """,
            'truncate': 'TRUNCATE `{table}`;',
        },
        'sqlite': {
            'populate': """

            INSERT INTO "{history}" (slug, object_type_id, object_id)
            SELECT model."{model_slug}",
                   %s,
                   model."{model_pk}"
              FROM "{model}" AS model;

            """,
            'truncate': 'DELETE FROM "{table}";',
        },
    }

    def populate(self, force=False, app_label=None, model_names=None):
        """
        Populates the slug history.
        """
        if force or self.count() <= 0:
            cursor = conn.cursor()
            if app_label is None:
                models = apps.get_models()

            app_config = apps.get_app_config(app_label)
            if model_names is None:
                models = app_config.get_models()
            else:
                models = [
                    app_config.get_model(name)
                    for name
                    in model_names
                ]

            with transaction.atomic():
                for model in models:
                    opts = model._meta
                    try:
                        slug_field = opts.get_field('slug')
                    except FieldDoesNotExist:
                        continue

                    if model == self.model:
                        continue

                    populate_sql = self.statements[conn.vendor]['populate'].format(
                        history=self.model._meta.db_table,
                        model=opts.db_table,
                        model_pk=opts.pk.column,
                        model_slug=slug_field.column,
                    )
                    object_type = ContentType.objects.get_for_model(model)
                    cursor.execute(populate_sql, [object_type.pk])

