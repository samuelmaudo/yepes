# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from datetime import date, datetime

from django.template import defaultfilters
from django.utils.formats import date_format
from django.utils.timezone import localtime
from django.utils.translation import ugettext as _


def naturalday(value, format=None):
    """
    For date values that are tomorrow, today or yesterday compared to
    present day returns representing string. Otherwise, returns a string
    formatted according to settings.DATE_FORMAT.
    """
    value = localtime(value)
    try:
        tzinfo = getattr(value, 'tzinfo', None)
        value = date(value.year, value.month, value.day)
    except AttributeError:
        # Passed value wasn't a date object.
        return value
    except ValueError:
        # Date arguments out of range.
        return value

    today = datetime.now(tzinfo).date()
    delta = value - today
    if delta.days > 7:
        return date_format(value, format)
    elif delta.days > 2:
        if value.weekday() == 0:
            return _('Next Monday')
        elif value.weekday() == 1:
            return _('Next Tuesday')
        elif value.weekday() == 2:
            return _('Next Wednesday')
        elif value.weekday() == 3:
            return _('Next Thursday')
        elif value.weekday() == 4:
            return _('Next Friday')
        elif value.weekday() == 5:
            return _('Next Saturday')
        else:
            return _('Next Sunday')
    elif delta.days == 2:
        return _('After tomorrow')
    elif delta.days == 1:
        return _('Tomorrow')
    elif delta.days == 0:
        return _('Today')
    elif delta.days == -1:
        return _('Yesterday')
    elif delta.days == -2:
        return _('Before yesterday')
    elif delta.days > -7:
        if value.weekday() == 0:
            return _('Last Monday')
        elif value.weekday() == 1:
            return _('Last Tuesday')
        elif value.weekday() == 2:
            return _('Last Wednesday')
        elif value.weekday() == 3:
            return _('Last Thursday')
        elif value.weekday() == 4:
            return _('Last Friday')
        elif value.weekday() == 5:
            return _('Last Saturday')
        else:
            return _('Last Sunday')
    else:
        return date_format(value, format)

