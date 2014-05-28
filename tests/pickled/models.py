# -*- coding:utf-8 -*-

from django.db import models

from yepes.fields import PickledObjectField


class TestModel(models.Model):

    default = PickledObjectField()
    protocol_0 = PickledObjectField(protocol=0)
    protocol_1 = PickledObjectField(protocol=1)
    protocol_2 = PickledObjectField(protocol=2)

