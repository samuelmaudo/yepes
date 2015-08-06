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

