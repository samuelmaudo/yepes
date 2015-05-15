# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class BooleanModel(models.Model):

    boolean = models.BooleanField()
    boolean_as_string = models.BooleanField()
    null_boolean = models.NullBooleanField()
    null_boolean_as_string = models.NullBooleanField()


class DateTimeModel(models.Model):

    date = models.DateField(
            blank=True,
            null=True)
    datetime = models.DateTimeField(
            blank=True,
            null=True)
    time = models.TimeField(
            blank=True,
            null=True)


class NumericModel(models.Model):

    integer = models.IntegerField(
            blank=True,
            null=True)
    integer_as_string = models.IntegerField(
            blank=True,
            null=True)
    float = models.FloatField(
            blank=True,
            null=True)
    float_as_string = models.FloatField(
            blank=True,
            null=True)
    decimal = models.DecimalField(
            blank=True,
            null=True,
            max_digits=8,
            decimal_places=2)
    decimal_as_string = models.DecimalField(
            blank=True,
            null=True,
            max_digits=8,
            decimal_places=2)


class TextModel(models.Model):

    char = models.CharField(
            blank=True,
            null=True,
            max_length=255)
    text = models.TextField(
            blank=True,
            null=True)


class AlphabetModel(models.Model):

    letter = models.CharField(
            max_length=1,
            unique=True)
    word = models.CharField(
            max_length=15,
            unique=True)


class AuthorModel(models.Model):

    name = models.CharField(
            max_length=255,
            unique=True)


class BlogModel(models.Model):

    name = models.CharField(
            max_length=255,
            unique=True)
    description = models.TextField(
            blank=True)


class BlogCategoryModel(models.Model):

    blog = models.ForeignKey(
            BlogModel,
            related_name='categories')
    name = models.CharField(
            max_length=255)
    description = models.TextField(
            blank=True)

    class Meta:
        unique_together = ('blog', 'name')


class PostModel(models.Model):

    title = models.CharField(
            max_length=255)
    author = models.ForeignKey(
            AuthorModel,
            related_name='posts')
    category = models.ForeignKey(
            BlogCategoryModel,
            related_name='posts')
    content = models.TextField(
            blank=True)

