# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('standards', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geographicarea',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation Date'),
        ),
        migrations.AlterField(
            model_name='geographicarea',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last Modified'),
        ),
    ]
