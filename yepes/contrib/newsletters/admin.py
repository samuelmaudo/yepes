# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.conf.urls import url
from django.db import models
from django.db.models import F, Q
from django.db.models import Count
from django.utils.html import format_html
from django.utils.six.moves.urllib.parse import urljoin
from django.utils.translation import ugettext_lazy as _

from yepes import admin
from yepes.apps import apps
from yepes.conf import settings
from yepes.utils.aggregates import SumIf

Bounce = apps.get_model('newsletters', 'Bounce')
Click = apps.get_model('newsletters', 'Click')
Delivery = apps.get_model('newsletters', 'Delivery')
Domain = apps.get_model('newsletters', 'Domain')
Message = apps.get_model('newsletters', 'Message')
MessageImage = apps.get_model('newsletters', 'MessageImage')
MessageLink = apps.get_model('newsletters', 'MessageLink')
Newsletter = apps.get_model('newsletters', 'Newsletter')
Open = apps.get_model('newsletters', 'Open')
Subscriber = apps.get_model('newsletters', 'Subscriber')
SubscriberTag = apps.get_model('newsletters', 'SubscriberTag')
Subscription = apps.get_model('newsletters', 'Subscription')
Unsubscription = apps.get_model('newsletters', 'Unsubscription')
UnsubscriptionReason = apps.get_model('newsletters', 'UnsubscriptionReason')

DispatchView = apps.get_class('newsletters.views', 'DispatchView')


class StatisticsMixin(object):

    def admin_bounce_count(self, obj):
        return getattr(obj, 'bounce_count', 0)
    admin_bounce_count.admin_order_field = 'bounce_count'
    admin_bounce_count.short_description = _('Bounces')

    def admin_click_count(self, obj):
        return getattr(obj, 'click_count', 0)
    admin_click_count.admin_order_field = 'click_count'
    admin_click_count.short_description = _('Clicks')

    def admin_delivery_count(self, obj):
        return getattr(obj, 'delivery_count', 0)
    admin_delivery_count.admin_order_field = 'delivery_count'
    admin_delivery_count.short_description = _('Deliveries')

    def admin_open_count(self, obj):
        return getattr(obj, 'open_count', 0)
    admin_open_count.admin_order_field = 'open_count'
    admin_open_count.short_description = _('Opens')

    def admin_subscriber_count(self, obj):
        return getattr(obj, 'subscriber_count', 0)
    admin_subscriber_count.admin_order_field = 'subscriber_count'
    admin_subscriber_count.short_description = _('Subscribers')

    def admin_subscription_count(self, obj):
        return getattr(obj, 'subscription_count', 0)
    admin_subscription_count.admin_order_field = 'subscription_count'
    admin_subscription_count.short_description = _('Subscriptions')

    def admin_unsubscription_count(self, obj):
        return getattr(obj, 'unsubscription_count', 0)
    admin_unsubscription_count.admin_order_field = 'unsubscription_count'
    admin_unsubscription_count.short_description = _('Unsubscriptions')


class BounceAdminForm(forms.ModelForm):

    body = forms.CharField(
        label=_('Body'),
        widget=forms.Textarea(attrs={
            'class': 'vLargeTextField',
            'style':'height:290px',
        }))

    class Meta:
        model = Bounce
        fields = []


class BounceAdmin(admin.ModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  ['subscriber', 'message'],
        'm2m': [],
    }
    date_hierarchy = 'date'
    fieldsets = [
        (None, {
            'fields': [
                'message',
                'subscriber',
                'date',
            ],
        }),
        (_('Details'), {
            'classes': [
                'grp-collapse',
                'grp-open',
            ],
            'fields': [
                'header',
                'body',
            ]
        }),
    ]
    form = BounceAdminForm
    list_display = [
        'message',
        'subscriber',
        'date',
    ]
    raw_id_fields = [
        'subscriber',
        'message',
    ]
    search_fields = [
        'subscriber__email_address',
    ]

    def get_queryset(self, request):
        qs = super(BounceAdmin, self).get_queryset(request)
        qs = qs.prefetch_related(
            'message',
            'subscriber',
        )
        return qs


class ClickAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'date',
                'subscriber',
                'message',
                'link',
            ],
        }),
    ]
    list_display = [
        'link',
        'message',
        'subscriber',
        'date',
    ]
    readonly_fields = [
        'link',
        'message',
        'subscriber',
        'date',
    ]
    search_fields = [
        'subscriber__email_address',
    ]

    def get_queryset(self, request):
        qs = super(ClickAdmin, self).get_queryset(request)
        qs = qs.prefetch_related(
            'link',
            'message',
            'subscriber',
        )
        return qs


class DeliveryAdmin(admin.ModelAdmin):

    change_list_template = 'admin/change_list_filter_sidebar.html'
    change_list_filter_template = 'admin/filter_listing.html'
    date_hierarchy = 'date'
    fieldsets = [
        (None, {
            'fields': [
                'admin_status',
                'subscriber',
                'message',
            ],
        }),
        (_('Timing'), {
            'classes': [
                'grp-collapse',
                'grp-open',
            ],
            'fields': [
                'date',
                'process_date',
                'bounce_date',
                'open_date',
                'click_date',
            ]
        }),
    ]
    list_display = [
        'message',
        'subscriber',
        'admin_status',
    ]
    list_filter = [
        'is_processed',
        'is_bounced',
        'is_opened',
        'is_clicked',
    ]
    readonly_fields = [
        'admin_status',
        'bounce_date',
        'click_date',
        'date',
        'message',
        'open_date',
        'process_date',
        'subscriber',
    ]
    search_fields = [
        'subscriber__email_address',
    ]

    def admin_status(self, obj):
        pattern = '<span style="color:{0}">{1}</span>'
        if obj.is_bounced:
            color = '#DE2121'
            text = _('Bounced')
        elif obj.is_clicked:
            color = '#42AD3F'
            text = _('Clicked')
        elif obj.is_opened:
            color = '#42AD3F'
            text = _('Opened')
        elif obj.is_processed:
            color = '#42AD3F'
            text = _('Dispatched')
        else:
            color = '#EE9A31'
            text = _('Pending')
        return format_html(pattern, color, text)
    admin_status.allow_tags = True
    admin_status.short_description = _('Status')

    def get_queryset(self, request):
        qs = super(DeliveryAdmin, self).get_queryset(request)
        qs = qs.prefetch_related(
            'message',
            'subscriber',
        )
        return qs


class DomainAdmin(StatisticsMixin, admin.ModelAdmin):

    #change_list_template = 'admin/change_list_filter_sidebar.html'
    change_list_filter_template = 'admin/filter_listing.html'
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'is_trusted',
            ],
        }),
    ]
    list_display = [
        'admin_name',
        'admin_delivery_count',
        'admin_open_count',
        'admin_click_count',
        'admin_bounce_count',
    ]
    list_filter = [
        'is_trusted',
    ]
    readonly_fields = [
        'name',
    ]
    search_fields = [
        'name',
    ]

    def admin_name(self, obj):
        if not obj.is_trusted:
            return obj.name
        else:
            return format_html(
                '{0} <img src="{1}" alt="({2})">',
                obj.name,
                urljoin(settings.STATIC_URL, 'admin/img/icon-yes.gif'),
                _('Trusted'))
    admin_name.admin_order_field = 'name'
    admin_name.allow_tags = True
    admin_name.short_description = _('Domain')

    def get_queryset(self, request):
        qs = super(DomainAdmin, self).get_queryset(request)
        qs = qs.annotate(
            bounce_count=SumIf(1, Q(deliveries__is_bounced=True)),
            click_count=SumIf(1, Q(deliveries__is_clicked=True)),
            delivery_count=SumIf(1, Q(deliveries__is_processed=True)),
            open_count=SumIf(1, Q(deliveries__is_opened=True)),
        )
        return qs


class MessageAdminForm(forms.ModelForm):

    html = forms.CharField(
        label=_('HTML Version'),
        widget=forms.Textarea(attrs={
            'class': 'vLargeTextField',
            'style':'height:290px',
        }))
    text = forms.CharField(
        label=_('Plain Text Version'),
        widget=forms.Textarea(attrs={
            'class': 'vLargeTextField',
            'style':'height:290px',
        }),
        required=False)

    class Meta:
        model = Message
        fields = []


class MessageAdmin(StatisticsMixin, admin.ModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  ['newsletter'],
        'm2m': [],
    }
    change_form_template = 'admin/newsletters/message/change_form.html'
    fieldsets = [
        (None, {
            'fields': [
                'guid',
                'newsletter',
                'subject',
                'slug',
                'html',
                'text',
            ],
        }),
    ]
    form = MessageAdminForm
    list_display = [
        'admin_subject',
        'admin_delivery_count',
        'admin_open_count',
        'admin_click_count',
        'admin_bounce_count',
    ]
    list_filter = [
        'newsletter',
    ]
    prepopulated_fields = {
        'slug': ('subject', ),
    }
    raw_id_fields = [
        'newsletter',
    ]
    readonly_fields = [
        'guid',
    ]
    search_fields = [
        'subject',
    ]

    def admin_subject(self, obj):
        if not obj.is_sent:
            return obj.subject
        else:
            return format_html(
                '{0} <img src="{1}" alt="({2})">',
                obj.subject,
                urljoin(settings.STATIC_URL, 'admin/img/icon-yes.gif'),
                _('Sent'))
    admin_subject.admin_order_field = 'subject'
    admin_subject.allow_tags = True
    admin_subject.short_description = _('Name')

    def get_queryset(self, request):
        qs = super(MessageAdmin, self).get_queryset(request)
        qs = qs.annotate(
            bounce_count=SumIf(1, Q(deliveries__is_bounced=True)),
            click_count=SumIf(1, Q(deliveries__is_clicked=True)),
            delivery_count=SumIf(1, Q(deliveries__is_processed=True)),
            open_count=SumIf(1, Q(deliveries__is_opened=True)),
        )
        return qs

    def get_urls(self):
        info = (self.model._meta.app_label, self.model._meta.model_name)
        urls = [
            url(r'^(?P<pk>\d+)/dispatch/$',
                self.admin_site.admin_view(DispatchView.as_view()),
                name='{0}_{1}_dispatch'.format(*info),
            ),
        ]
        return urls + super(MessageAdmin, self).get_urls()


class MessageImageAdmin(admin.IllustratedMixin, admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'guid',
                'image',
                'name',
            ],
        }),
    ]
    list_display = [
        'admin_image',
        'name',
        'last_modified',
        'creation_date',
    ]
    list_display_links = [
        'admin_image',
        'name',
    ]
    readonly_fields = [
        'guid',
    ]
    search_fields = [
        'name',
    ]


class MessageLinkAdmin(StatisticsMixin, admin.ReadOnlyMixin, admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'guid',
                'url',
            ],
        }),
    ]
    list_display = [
        'url',
        'admin_click_count',
        'creation_date',
    ]
    readonly_fields = [
        'guid',
        'url',
    ]
    search_fields = [
        'url',
    ]

    def get_queryset(self, request):
        qs = super(MessageLinkAdmin, self).get_queryset(request)
        qs = qs.annotate(click_count=Count('clicks'))
        return qs


class NewsletterAdmin(StatisticsMixin, admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'guid',
                'name',
                'slug',
                'description',
                'is_published',
            ],
        }),
        (_('Metadata'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'meta_title',
                'meta_description',
                'meta_keywords',
            ]
        }),
        (_('Settings'), {
            'classes': [
                'grp-collapse',
                'grp-closed',
            ],
            'fields': [
                'connection',
                'sender_name',
                'sender_address',
                'reply_to_name',
                'reply_to_address',
                'return_path_name',
                'return_path_address',
            ]
        }),
    ]
    list_display = [
        'name',
        'admin_delivery_count',
        'admin_open_count',
        'admin_click_count',
        'admin_bounce_count',
        'admin_is_published',
        'index',
    ]
    list_editable = [
        'index',
    ]
    list_max_show_all = 100
    list_per_page = 50
    readonly_fields = [
        'guid',
    ]
    prepopulated_fields = {'slug': ('name', )}
    search_fields = [
        'name',
    ]

    def admin_is_published(self, obj):
        pattern = '<span style="color:{0}">{1}</span>'
        if obj.is_published:
            color = '#42AD3F'
            text = _('Published')
        else:
            color = '#EE9A31'
            text = _('Hidden')
        return format_html(pattern, color, text)
    admin_is_published.admin_order_field = 'is_published'
    admin_is_published.allow_tags = True
    admin_is_published.short_description = _('Status')

    def admin_reply_to(self, obj):
        if obj.reply_to_name:
            return '{0} <{1}>'.format(obj.reply_to_name, obj.reply_to_email)
        elif obj.reply_to_email:
            return obj.reply_to_email
        else:
            return ''
    admin_reply_to.admin_order_field = 'reply_to_email'
    admin_reply_to.short_description = _('Reply To')

    def admin_return_path(self, obj):
        if obj.return_path_name:
            return '{0} <{1}>'.format(obj.return_path_name, obj.return_path_email)
        elif obj.return_path_email:
            return obj.return_path_email
        else:
            return ''
    admin_return_path.admin_order_field = 'return_path_email'
    admin_return_path.short_description = _('Return Path')

    def admin_sender(self, obj):
        if obj.sender_name:
            return '{0} <{1}>'.format(obj.sender_name, obj.sender_email)
        elif obj.sender_email:
            return obj.sender_email
        else:
            return ''
    admin_sender.admin_order_field = 'sender_email'
    admin_sender.short_description = _('Sender')

    def get_queryset(self, request):
        qs = super(NewsletterAdmin, self).get_queryset(request)
        qs = qs.annotate(
            bounce_count=SumIf(1, Q(deliveries__is_bounced=True)),
            click_count=SumIf(1, Q(deliveries__is_clicked=True)),
            delivery_count=SumIf(1, Q(deliveries__is_processed=True)),
            open_count=SumIf(1, Q(deliveries__is_opened=True)),
        )
        return qs


class OpenAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'date',
                'subscriber',
                'message',
            ],
        }),
    ]
    list_display = [
        'message',
        'subscriber',
        'date',
    ]
    readonly_fields = [
        'message',
        'subscriber',
        'date',
    ]
    search_fields = [
        'subscriber__email_address',
    ]

    def get_queryset(self, request):
        qs = super(OpenAdmin, self).get_queryset(request)
        qs = qs.prefetch_related(
            'message',
            'subscriber',
        )
        return qs


class SubscriberAdminForm(forms.ModelForm):

    email_address = forms.CharField(
        label=_('E-mail Address'),
        max_length=127,
        widget=forms.TextInput(attrs={
            'class': 'vTextField',
            'style':'max-width:438px',
        }))

    class Meta:
        model = Subscriber
        fields = []


class SubscriberAdmin(admin.EnableableMixin, admin.ModelAdmin):

    autocomplete_lookup_fields = {
        'fk':  [],
        'm2m': ['tags'],
    }
    change_list_template = 'admin/change_list_filter_sidebar.html'
    #change_list_filter_template = 'admin/filter_listing.html'
    fieldsets = [
        (None, {
            'fields': [
                'guid',
                ('email_address', 'is_enabled'),
                'first_name',
                'last_name',
                'tags',
            ],
        }),
    ]
    form = SubscriberAdminForm
    list_display = [
        'email_address',
        'admin_score',
        'first_name',
        'last_name',
        'admin_enable_status',
        'admin_tags',
    ]
    list_filter = [
        'is_enabled',
        'email_domain',
        'tags',
    ]
    list_max_show_all = 100
    list_per_page = 50
    raw_id_fields = [
        'tags',
    ]
    readonly_fields = [
        'guid',
    ]
    search_fields = [
        'email_address',
        'first_name',
        'last_name',
    ]

    def admin_score(self, obj):
        return format_html(
            '<div style="background:transparent url(\'{0}\') repeat-x;'
                        'height:16px;'
                        'margin:-2px;'
                        'position:relative;'
                        'width:80px">'
            '<span style="background:transparent url(\'{1}\') repeat-x;'
                        'height:16px;'
                        'left:0;'
                        'position:absolute;'
                        'top:0;'
                        'width:{2}px">'
            '</span></div>',
            urljoin(settings.STATIC_URL, 'admin/img/icon-star-empty.png'),
            urljoin(settings.STATIC_URL, 'admin/img/icon-star.png'),
            obj.score * 16)
    admin_score.admin_order_field = 'score'
    admin_score.allow_tags = True
    admin_score.short_description = 'Score'

    def admin_tags(self, obj):
        links = [
            format_html('<a href="?tags__id__exact={0}">{1}</a>', tag.pk, tag)
            for tag
            in obj.tags.all()
        ]
        return ', '.join(links) if links else _('No tag')
    admin_tags.allow_tags = True
    admin_tags.short_description = _('Tags')

    def get_queryset(self, request):
        qs = super(SubscriberAdmin, self).get_queryset(request)
        qs = qs.prefetch_related('tags')
        return qs

    def save_model(self, request, obj, form, change):
        obj.set_email(form.cleaned_data['email_address'])
        obj.save()


class SubscriberTagAdmin(StatisticsMixin, admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'name',
                'description',
            ],
        }),
    ]
    list_display = [
        'name',
        'admin_subscriber_count',
    ]
    search_fields = [
        'name',
    ]

    def get_queryset(self, request):
        qs = super(SubscriberTagAdmin, self).get_queryset(request)
        qs = qs.annotate(subscriber_count=Count('subscribers'))
        return qs


class SubscriptionAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'subscriber',
                'newsletter',
                'date',
            ],
        }),
    ]
    list_display = [
        'subscriber',
        'newsletter',
        'date',
    ]
    readonly_fields = [
        'subscriber',
        'newsletter',
        'date',
    ]
    search_fields = [
        'subscriber__email_address',
    ]

    def get_queryset(self, request):
        qs = super(SubscriptionAdmin, self).get_queryset(request)
        qs = qs.prefetch_related(
            'subscriber',
            'newsletter',
        )
        return qs


class UnsubscriptionAdmin(admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'subscriber',
                'newsletter',
                'date',
                'reason',
                'last_message',
            ],
        }),
    ]
    list_display = [
        'subscriber',
        'newsletter',
        'date',
        'reason',
        'last_message',
    ]
    readonly_fields = [
        'subscriber',
        'newsletter',
        'date',
        'reason',
        'last_message',
    ]
    search_fields = [
        'subscriber__email_address',
    ]

    def get_queryset(self, request):
        qs = super(UnsubscriptionAdmin, self).get_queryset(request)
        qs = qs.prefetch_related(
            'subscriber',
            'newsletter',
            'reason',
            'last_message',
        )
        return qs


class UnsubscriptionReasonAdmin(StatisticsMixin, admin.ModelAdmin):

    fieldsets = [
        (None, {
            'fields': [
                'description',
            ],
        }),
        (_('Statistics'), {
            'classes': [
                'grp-collapse',
                'grp-open',
            ],
            'fields': [
                'admin_unsubscription_count',
            ],
        }),
    ]
    list_display = [
        'description',
        'admin_unsubscription_count',
        'index',
    ]
    list_editable = [
        'index',
    ]
    readonly_fields = [
        'admin_unsubscription_count',
    ]

    def get_queryset(self, request):
        qs = super(UnsubscriptionReasonAdmin, self).get_queryset(request)
        qs = qs.annotate(unsubscription_count=Count('unsubscriptions'))
        return qs


admin.site.register(Bounce, BounceAdmin)
admin.site.register(Click, ClickAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MessageImage, MessageImageAdmin)
admin.site.register(MessageLink, MessageLinkAdmin)
admin.site.register(SubscriberTag, SubscriberTagAdmin)
admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(Open, OpenAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Unsubscription, UnsubscriptionAdmin)
admin.site.register(UnsubscriptionReason, UnsubscriptionReasonAdmin)

