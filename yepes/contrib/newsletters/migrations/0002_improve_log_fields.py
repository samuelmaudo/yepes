# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletters', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation Date'),
        ),
        migrations.AlterField(
            model_name='message',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last Modified'),
        ),
        migrations.AlterField(
            model_name='messageimage',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation Date'),
        ),
        migrations.AlterField(
            model_name='messageimage',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last Modified'),
        ),
        migrations.AlterField(
            model_name='messagelink',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation Date'),
        ),
        migrations.AlterField(
            model_name='messagelink',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last Modified'),
        ),
        migrations.AlterField(
            model_name='newsletter',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation Date'),
        ),
        migrations.AlterField(
            model_name='newsletter',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last Modified'),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation Date'),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last Modified'),
        ),
        migrations.AlterField(
            model_name='subscribertag',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation Date'),
        ),
        migrations.AlterField(
            model_name='subscribertag',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last Modified'),
        ),
    ]
