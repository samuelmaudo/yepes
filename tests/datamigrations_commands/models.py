# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class Alphabet(models.Model):

    letter = models.CharField(
            max_length=1,
            unique=True)
    word = models.CharField(
            max_length=15,
            unique=True)


class Author(models.Model):

    name = models.CharField(
            max_length=255,
            unique=True)


class Category(models.Model):

    name = models.CharField(
            max_length=255,
            unique=True)
    description = models.TextField(
            blank=True)


class Tag(models.Model):

    name = models.CharField(
            max_length=255,
            unique=True)


class Post(models.Model):

    title = models.CharField(
            max_length=255,
            unique=True)
    content = models.TextField(
            blank=True)

    author = models.ForeignKey(
            Author,
            on_delete=models.CASCADE,
            related_name='posts')
    category = models.ForeignKey(
            Category,
            on_delete=models.CASCADE,
            related_name='posts')
    tags = models.ManyToManyField(
            Tag,
            blank=True,
            related_name='posts')

