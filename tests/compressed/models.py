# -*- coding:utf-8 -*-

from django.db import models

from yepes.fields import CompressedTextField


class TestModel(models.Model):

    default = CompressedTextField()
    level_3 = CompressedTextField(compression_level=3)
    level_6 = CompressedTextField(compression_level=6)
    level_9 = CompressedTextField(compression_level=9)

