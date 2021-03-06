# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.contrib.admin import widgets
from django.utils.translation import ugettext_lazy as _

from yepes.apps import apps
from yepes.forms import fields

Newsletter = apps.get_model('newsletters', 'Newsletter')
UnsubscriptionReason = apps.get_model('newsletters', 'UnsubscriptionReason')


FILTER_CHOICES = [
    ('', '---------'),
    ('gte', _('is greather than or equal to')),
    ('gt', _('is greather than')),
    ('exact', _('is equal to')),
    ('lt', _('is less than')),
    ('lte', _('is less than or equal to')),
]

class DispatchForm(forms.Form):

    date = forms.SplitDateTimeField(
            label=_('Dispatch From'),
            widget=widgets.AdminSplitDateTime)
    score_filter = forms.ChoiceField(
            choices=FILTER_CHOICES,
            label=_('Subscriber Score'),
            required=False)
    score_filter_value = forms.TypedChoiceField(
            choices=[
                (0, '0'),
                (1, '1'),
                (2, '2'),
                (3, '3'),
                (4, '4'),
                (5, '5'),
            ],
            label='',
            required=False)
    bounce_filter = forms.ChoiceField(
            choices=FILTER_CHOICES,
            label=_('Subscriber Bounces'),
            required=False)
    bounce_filter_value = forms.IntegerField(
            label='',
            required=False)
    click_filter = forms.ChoiceField(
            choices=FILTER_CHOICES,
            label=_('Subscriber Clicks'),
            required=False)
    click_filter_value = forms.IntegerField(
            label='',
            required=False)
    open_filter = forms.ChoiceField(
            choices=FILTER_CHOICES,
            label=_('Subscriber Opens'),
            required=False)
    open_filter_value = forms.IntegerField(
            label='',
            required=False)
    tags_filter = forms.ChoiceField(
            choices=[
                ('', '---------'),
                ('eq', _('includes')),
                ('ne', _('does not include')),
            ],
            label=_('Subscriber Tags'),
            required=False)
    tags_filter_value = forms.IntegerField(
            label='',
            required=False)


class ProfileForm(forms.Form):

    email_address = fields.EmailField(
            label=_('E-mail Address'),
            max_length=120)
    first_name = forms.CharField(
            label=_('First Name'),
            max_length=60,
            required=False)
    last_name = forms.CharField(
            label=_('Last Name'),
            max_length=60,
            required=False)
    #newsletters = forms.ModelMultipleChoiceField(
            #label=_('Newsletters'),
            #queryset=Newsletter.objects.get_queryset(),
            #widget=forms.CheckboxSelectMultiple)


class SubscriptionForm(forms.Form):

    newsletter = forms.ModelChoiceField(
            label=_('Newsletter'),
            queryset=Newsletter.objects.get_queryset())
    email_address = fields.EmailField(
            label=_('E-mail Address'),
            max_length=120)
    first_name = forms.CharField(
            label=_('First Name'),
            max_length=60,
            required=False)
    last_name = forms.CharField(
            label=_('Last Name'),
            max_length=60,
            required=False)


class UnsubscriptionForm(forms.Form):

    newsletter = forms.ModelChoiceField(
            label=_('Newsletter'),
            queryset=Newsletter.objects.get_queryset())
    email_address = fields.EmailField(
            label=_('E-mail Address'),
            max_length=120)


class UnsubscriptionReasonForm(forms.Form):

    reason = forms.ModelChoiceField(
            empty_label=None,
            label=_('Reason'),
            queryset=UnsubscriptionReason.objects.get_queryset(),
            widget=forms.RadioSelect)

