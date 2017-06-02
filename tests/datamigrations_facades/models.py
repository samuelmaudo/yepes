# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models


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


class CategoryModel(models.Model):

    name = models.CharField(
            max_length=255,
            unique=True)
    description = models.TextField(
            blank=True)


class PostModel(models.Model):

    title = models.CharField(
            max_length=255,
            unique=True)
    author = models.ForeignKey(
            AuthorModel,
            on_delete=models.CASCADE,
            related_name='posts')
    category = models.ForeignKey(
            CategoryModel,
            on_delete=models.CASCADE,
            related_name='posts')
    content = models.TextField(
            blank=True)

