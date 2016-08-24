# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import yepes.contrib.standards.fields
import mptt.fields
import django.db.models.deletion
import django.contrib.sites.managers
import yepes.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '__first__'),
        ('standards', '0001_initial'),
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='Browser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', yepes.fields.IntegerField(min_value=0, null=True, verbose_name='Index', blank=True)),
                ('name', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Name')),
                ('token', yepes.fields.CharField(help_text='Used to check the User-Agent strings.', max_length=255, verbose_name='Token')),
                ('regex', yepes.fields.BooleanField(default=False, help_text='Check this if your token is a regular expression.', verbose_name='Regular Expression')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='Parent', to='metrics.Browser', null=True)),
            ],
            options={
                'ordering': ['index'],
                'verbose_name': 'Browser',
                'verbose_name_plural': 'Browsers',
            },
        ),
        migrations.CreateModel(
            name='Engine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', yepes.fields.IntegerField(min_value=0, null=True, verbose_name='Index', blank=True)),
                ('name', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Name')),
                ('token', yepes.fields.CharField(help_text='Used to check the User-Agent strings.', max_length=255, verbose_name='Token')),
                ('regex', yepes.fields.BooleanField(default=False, help_text='Check this if your token is a regular expression.', verbose_name='Regular Expression')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='Parent', to='metrics.Engine', null=True)),
            ],
            options={
                'ordering': ['index'],
                'verbose_name': 'Rendering Engine',
                'verbose_name_plural': 'Rendering Engines',
            },
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', yepes.fields.IntegerField(min_value=0, null=True, verbose_name='Index', blank=True)),
                ('name', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Name')),
                ('token', yepes.fields.CharField(help_text='Used to check the User-Agent strings.', max_length=255, verbose_name='Token')),
                ('regex', yepes.fields.BooleanField(default=False, help_text='Check this if your token is a regular expression.', verbose_name='Regular Expression')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='Parent', to='metrics.Platform', null=True)),
            ],
            options={
                'ordering': ['index'],
                'verbose_name': 'Platform',
                'verbose_name_plural': 'Platforms',
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site', models.ForeignKey(related_name='pages', verbose_name='Site', to='sites.Site')),
                ('path_head', yepes.fields.CharField(max_length=255, verbose_name='Path Head', blank=True)),
                ('path_tail', yepes.fields.CharField(max_length=63, verbose_name='Path Tail')),
                ('query_string', yepes.fields.CharField(max_length=255, verbose_name='Query String', blank=True)),
            ],
            options={
                'ordering': ['path_head', 'path_tail', 'query_string'],
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
            },
            managers=[
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.CreateModel(
            name='Referrer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Domain')),
            ],
            options={
                'ordering': ['domain'],
                'verbose_name': 'Referrer',
                'verbose_name_plural': 'Referrers',
            },
        ),
        migrations.CreateModel(
            name='ReferrerPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('referrer', models.ForeignKey(related_name='pages', verbose_name='Referrer', to='metrics.Referrer')),
                ('full_path', yepes.fields.CharField(max_length=255, verbose_name='Path')),
            ],
            options={
                'ordering': ['full_path'],
                'verbose_name': 'Referrer page',
                'verbose_name_plural': 'Referrer pages',
            },
        ),
        migrations.CreateModel(
            name='Visitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site', models.ForeignKey(related_name='visitors', verbose_name='Site', to='sites.Site')),
                ('is_authenticated', yepes.fields.BooleanField(verbose_name='Is Authenticated?')),
                ('key', yepes.fields.CharField(max_length=32, verbose_name='Visitor Key', db_index=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'Visitor',
                'verbose_name_plural': 'Visitors',
            },
            managers=[
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site', models.ForeignKey(related_name='visits', verbose_name='Site', to='sites.Site')),
                ('visitor', models.ForeignKey(related_name='visits', verbose_name='Visitor', to='metrics.Visitor')),
                ('country', yepes.contrib.standards.fields.CountryField(related_name='visits', on_delete=django.db.models.deletion.PROTECT, verbose_name='Country', to='standards.Country', null=True)),
                ('language', yepes.contrib.standards.fields.LanguageField(related_name='visits', on_delete=django.db.models.deletion.PROTECT, verbose_name='Language', to='standards.Language', null=True)),
                ('region', yepes.contrib.standards.fields.RegionField(related_name='visits', on_delete=django.db.models.deletion.PROTECT, verbose_name='Region', to='standards.Region', null=True)),
                ('browser', models.ForeignKey(related_name='visits', verbose_name='Browser', to='metrics.Browser', null=True)),
                ('engine', models.ForeignKey(related_name='visits', verbose_name='Engine', to='metrics.Engine', null=True)),
                ('platform', models.ForeignKey(related_name='visits', verbose_name='Platform', to='metrics.Platform', null=True)),
                ('referrer', models.ForeignKey(related_name='visits', verbose_name='Referrer', to='metrics.Referrer', null=True)),
                ('referrer_page', models.ForeignKey(related_name='visits', verbose_name='Referrer Page', to='metrics.ReferrerPage', null=True)),
                ('page_count', yepes.fields.SmallIntegerField(default=0, verbose_name='Page Views')),
                ('start_date', models.DateTimeField(verbose_name='Start Date', db_index=True)),
                ('end_date', models.DateTimeField(verbose_name='End Date', db_index=True)),
                ('user_agent', yepes.fields.CharField(max_length=255, verbose_name='User-Agent')),
            ],
            options={
                'ordering': ['-start_date'],
                'verbose_name': 'Visit',
                'verbose_name_plural': 'Visits',
            },
            managers=[
                ('objects', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.CreateModel(
            name='PageView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('visit', models.ForeignKey(related_name='page_views', verbose_name='Visit', to='metrics.Visit')),
                ('page', models.ForeignKey(related_name='page_views', verbose_name='Page', to='metrics.Page')),
                ('previous_page_id', yepes.fields.IntegerField(null=True, verbose_name='Previous Page ID', blank=True)),
                ('next_page_id', yepes.fields.IntegerField(null=True, verbose_name='Next Page ID', blank=True)),
                ('status_code', yepes.fields.SmallIntegerField(default=0, verbose_name='Status Code')),
                ('date', models.DateTimeField(verbose_name='Date')),
                ('load_time', yepes.fields.FloatField(default=0.0, verbose_name='Load Time')),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'Page View',
                'verbose_name_plural': 'Page Views',
            },
        ),
        migrations.AddField(
            model_name='visit',
            name='pages',
            field=models.ManyToManyField(related_name='visits', verbose_name='Page Views', to='metrics.Page', through='metrics.PageView', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='referrerpage',
            unique_together=set([('referrer', 'full_path')]),
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('site', 'path_head', 'path_tail', 'query_string')]),
        ),
    ]
