# -*- coding:utf-8 -*-

from django.core.exceptions import ValidationError
from django.forms import TypedMultipleChoiceField

from yepes.forms.widgets import BitWidget
from yepes.types import Bit


class BitField(TypedMultipleChoiceField):

    def __init__(self, widget=BitWidget, *args, **kwargs):
        if not isinstance(widget, type):
            if not isinstance(widget, BitWidget):
                widget = BitWidget
        elif not issubclass(widget, BitWidget):
            widget = BitWidget
        kwargs['coerce'] = Bit
        kwargs['widget'] = widget
        super(BitField, self).__init__(*args, **kwargs)

    def validate(self, value):
        if self.required and not value:
            msg = self.error_messages['required']
            raise ValidationError(msg)

        for v in value:
            for key, verbose in self.choices:
                if v == key:
                    break
            else:
                msg = self.error_messages['invalid_choice']
                raise ValidationError(msg % {'value': v})

