# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.forms.formsets import BaseFormSet, DEFAULT_MAX_NUM
from django.utils import six

from yepes.admin.operations import Operation


class OperationChoiceField(forms.ChoiceField):

    def __init__(self, operations, required=True, widget=None, label=None,
                 initial=None, help_text='', *args, **kwargs):
        choices=[
            (op.label, op.label)
            for op
            in operations
        ]
        super(OperationChoiceField, self).__init__(
            choices=choices,
            required=required, widget=widget, label=label,
            initial=initial, help_text=help_text, *args, **kwargs
        )
        self.operations = operations

    def to_python(self, value):
        if value in self.empty_values:
            return None

        for op in self.operations:
            if value == op.label:
                return op

        return None

    def validate(self, value):
        return super(OperationChoiceField, self).validate(value.label)


class MassUpdateErrorList(forms.util.ErrorList):
    """
    Stores all errors for the form/formsets in a mass-update view.
    """
    def __init__(self, formset):
        if formset.is_bound:
            for errors in formset.errors:
                self.extend(list(six.itervalues(errors)))


class MassUpdateForm(forms.Form):

    update = forms.BooleanField(required=False)

    @property
    def errors(self):
        if self._errors is None:
            self.full_clean()
            if not self.cleaned_data['update']:
                self._errors.clear()
            else:
                op = self.cleaned_data['operation']
                if op is not None and not op.needs_value:
                    self._errors.clear()

        return self._errors


class MassUpdateFormSet(BaseFormSet):

    absolute_max = DEFAULT_MAX_NUM * 2
    can_delete = False
    can_order = False
    extra = 0
    form = MassUpdateForm
    max_num = DEFAULT_MAX_NUM
    validate_max = False

    def __init__(self, **kwargs):
        self.request = kwargs.pop('request')
        self.modeladmin = kwargs.pop('modeladmin')
        self.fields = self.modeladmin.get_formfields(self.request, many_to_many=True)
        super(MassUpdateFormSet, self).__init__(**kwargs)

    def add_fields(self, form, index):
        model_field, form_field = self.fields[index]

        # This prevent default values
        form_field.initial = None

        # This hack is necessary because autocomplete fields only work
        # if their id has this format: 'id_{field_name}'
        widget = form_field.widget
        widget_id = 'id_{0}'.format(model_field.name)
        widget.attrs['id'] = widget_id
        if isinstance(widget, forms.MultiWidget):
            for w in widget.widgets:
                w.attrs['id'] = w.id_for_label(widget_id)

        ops=self.modeladmin.get_field_operations(self.request, model_field)
        form.field = model_field
        form.fields['operation'] = OperationChoiceField(operations=ops)
        form.fields['value'] = form_field
        super(MassUpdateFormSet, self).add_fields(form, index)

    def is_multipart(self):
        if self.forms:
            return any(form.is_multipart() for form in self.forms)
        else:
            return self.empty_form.is_multipart()

    def total_form_count(self):
        return len(self.fields)

    @property
    def media(self):
        if self.forms:
            base = self.forms[0].media
            return sum((
                form.media
                for form
                in self.forms[1:]
            ), base)
        else:
            return self.empty_form.media

