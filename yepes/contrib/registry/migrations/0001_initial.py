# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.sites.managers


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '__first__'),
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=63, verbose_name='Key')),
                ('value', models.CharField(max_length=255, null=True, verbose_name='Value', blank=True)),
                ('site', models.ForeignKey(verbose_name='Site', to='sites.Site')),
            ],
            options={
                'verbose_name': 'Entry',
                'verbose_name_plural': 'Entries',
            },
            managers=[
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.CreateModel(
            name='LongEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=63, verbose_name='Key')),
                ('value', models.TextField(null=True, verbose_name='Value', blank=True)),
                ('site', models.ForeignKey(verbose_name='Site', to='sites.Site')),
            ],
            options={
                'verbose_name': 'Long Entry',
                'verbose_name_plural': 'Long Entries',
            },
            managers=[
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='entry',
            unique_together=set([('site', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='longentry',
            unique_together=set([('site', 'key')]),
        ),
    ]
