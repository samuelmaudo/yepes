# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes.contrib import datamigrations as migrations


class BooleanMigration(migrations.BaseModelMigration):

    fields = [
        migrations.BooleanField('boolean'),
        migrations.BooleanField('boolean_as_string', force_string=True),
        migrations.BooleanField('null_boolean'),
        migrations.BooleanField('null_boolean_as_string', force_string=True),
    ]


class DateTimeMigration(migrations.BaseModelMigration):

    fields = [
        migrations.DateField('date'),
        migrations.YearField('date__year'),
        migrations.MonthField('date__month'),
        migrations.DayField('date__day'),
        migrations.DateTimeField('datetime'),
        migrations.YearField('datetime__year'),
        migrations.MonthField('datetime__month'),
        migrations.DayField('datetime__day'),
        migrations.HourField('datetime__hour'),
        migrations.MinuteField('datetime__minute'),
        migrations.SecondField('datetime__second'),
        migrations.MicrosecondField('datetime__microsecond'),
        migrations.TimeZoneField('datetime__tzinfo'),
        migrations.TimeField('time'),
        migrations.HourField('time__hour'),
        migrations.MinuteField('time__minute'),
        migrations.SecondField('time__second'),
        migrations.MicrosecondField('time__microsecond'),
        migrations.TimeZoneField('time__tzinfo'),
    ]


class DateTimeEdgeMigration(migrations.BaseModelMigration):

    fields = [
        migrations.DateTimeField('date', 'date__datetime'),
        migrations.YearField('date', 'date__year'),
        migrations.MonthField('date', 'date__month'),
        migrations.DayField('date', 'date__day'),
        migrations.DateField('datetime', 'datetime__date'),
        migrations.TimeField('datetime', 'datetime__time'),
        migrations.YearField('datetime', 'datetime__year'),
        migrations.MonthField('datetime', 'datetime__month'),
        migrations.DayField('datetime', 'datetime__day'),
        migrations.HourField('datetime', 'datetime__hour'),
        migrations.MinuteField('datetime', 'datetime__minute'),
        migrations.SecondField('datetime', 'datetime__second'),
        migrations.MicrosecondField('datetime', 'datetime__microsecond'),
        migrations.TimeZoneField('datetime', 'datetime__tzinfo'),
        migrations.HourField('time', 'time__hour'),
        migrations.MinuteField('time', 'time__minute'),
        migrations.SecondField('time', 'time__second'),
        migrations.MicrosecondField('time', 'time__microsecond'),
        migrations.TimeZoneField('time', 'time__tzinfo'),
    ]


class FileMigration(migrations.BaseModelMigration):

    fields = [
        migrations.FileField('file'),
        migrations.FileField('image'),
    ]


class NumericMigration(migrations.BaseModelMigration):

    fields = [
        migrations.IntegerField('integer'),
        migrations.IntegerField('integer_as_string', force_string=True),
        migrations.FloatField('float'),
        migrations.FloatField('float_as_string', force_string=True),
        migrations.NumberField('decimal'),
        migrations.NumberField('decimal_as_string', force_string=True),
    ]


class TextMigration(migrations.BaseModelMigration):

    fields = [
        migrations.TextField('char'),
        migrations.TextField('text'),
    ]


class AlphabetMigration(migrations.BaseModelMigration):

    fields = [
        migrations.IntegerField('pk'),
        migrations.TextField('letter'),
        migrations.TextField('word'),
    ]


class AuthorMigration(migrations.BaseModelMigration):

    fields = [
        migrations.TextField('name'),
        migrations.FileField('image'),
    ]


class BlogMigration(migrations.BaseModelMigration):

    fields = [
        migrations.TextField('name'),
        migrations.TextField('description'),
    ]


class BlogCategoryMigration(migrations.BaseModelMigration):

    fields = [
        migrations.TextField('blog__name'),
        migrations.TextField('name'),
        migrations.TextField('description'),
    ]

