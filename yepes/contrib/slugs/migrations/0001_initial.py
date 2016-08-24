# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '__first__'),
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='SlugHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.CharField(verbose_name='Slug', max_length=255, editable=False, db_index=True)),
                ('object_id', models.PositiveIntegerField(verbose_name='Object ID', editable=False, db_index=True)),
                ('object_type', models.ForeignKey(editable=False, to='contenttypes.ContentType', verbose_name='Object Type')),
            ],
            options={
                'ordering': ['-pk'],
                'verbose_name': 'Slug Entry',
                'verbose_name_plural': 'Slug Entries',
            },
        ),
    ]
