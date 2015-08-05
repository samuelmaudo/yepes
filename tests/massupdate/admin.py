# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from yepes import admin

from .models import MassUpdateModel


class MassUpdateAdmin(admin.ModelAdmin):
    pass


admin.site.register(MassUpdateModel, MassUpdateAdmin)
