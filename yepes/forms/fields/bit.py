# -*- coding:utf-8 -*-

from django.forms import ChoiceField, MultipleChoiceField

from yepes.forms.widgets import BitWidget
from yepes.types import Bit
from yepes.utils.properties import cached_property


class BitField(MultipleChoiceField):

    def __init__(self, choices=(), widget=BitWidget, *args, **kwargs):
        if isinstance(widget, type):
            widget = widget()
        if not isinstance(widget, BitWidget):
            widget = BitWidget()
        super(ChoiceField, self).__init__(*args, **kwargs)
        self._choices = choices
        self.widget = widget

    @cached_property
    def choices(self):
        # ``choices`` can be any iterable, but is necessary to convert it into
        # a list because it will be consumed more than once.
        #
        # Django implementation calls list() when setting choices but this
        # implementation allows for lazy evaluation of the iterable.
        #
        return list(self._choices)

    def to_python(self, value):
        return Bit(value)

    def valid_value(self, value):
        for k, v in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if value == k2:
                        return True

            elif value == k:
                return True

        return False

