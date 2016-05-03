# -*- coding:utf-8 -*-

from django.contrib.sites.shortcuts import get_current_site

def current_site(request):
    """
    Returns the current site as context variable.
    """
    return {'current_site': get_current_site(request)}
