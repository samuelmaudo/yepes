# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletters', '0002_improve_log_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='meta_description',
        ),
        migrations.RemoveField(
            model_name='message',
            name='meta_keywords',
        ),
        migrations.RemoveField(
            model_name='message',
            name='meta_title',
        ),
        migrations.AddField(
            model_name='newsletter',
            name='canonical_url',
            field=models.URLField(blank=True, help_text="Optional URL to be used in the canonical meta tag. If left blank, the object's URL will be used.", max_length=255, verbose_name='Canonical URL'),
        ),
        migrations.AddField(
            model_name='newsletter',
            name='meta_index',
            field=models.NullBooleanField(choices=[(None, 'Default'), (True, 'index'), (False, 'noindex')], default=None, verbose_name='Robots'),
        ),
    ]
