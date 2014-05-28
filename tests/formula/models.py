# -*- coding:utf-8 -*-

from django.db import models

from yepes.fields import FormulaField


class TestModel(models.Model):

    permissive_formula = FormulaField(
            blank=True)
    restricted_formula = FormulaField(
            blank=True,
            variables=('x', 'y', 'z'))

    class Meta:
        ordering = ['id']

