# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.apps import apps
from yepes.cache import LookupTable
from yepes.contrib.registry import registry
from yepes.loading import LazyModel
from yepes.model_mixins import (
    Enableable,
    Illustrated,
    Logged,
    MetaData,
    Orderable,
    Slugged,
)
from yepes.utils.emails import normalize_email, validate_email
from yepes.utils.html import extract_text
from yepes.utils.properties import described_property
from yepes.validators.email import DOMAIN_RE

NewsletterManager = apps.get_class('newsletters.managers', 'NewsletterManager')

Delivery = LazyModel('newsletters', 'Delivery')
Domain = LazyModel('newsletters', 'Domain')


class AbstractBounce(models.Model):

    message = models.ForeignKey(
            'Message',
            on_delete=models.CASCADE,
            related_name='bounces',
            verbose_name=_('Message'))
    newsletter = models.ForeignKey(
            'Newsletter',
            on_delete=models.CASCADE,
            related_name='bounces',
            verbose_name=_('Newsletter'))
    subscriber = models.ForeignKey(
            'Subscriber',
            null=True,
            on_delete=models.SET_NULL,
            related_name='bounces',
            verbose_name=_('Subscriber'))
    domain = models.ForeignKey(
            'Domain',
            null=True,
            on_delete=models.SET_NULL,
            related_name='bounces',
            verbose_name=_('E-mail Domain'))

    date = models.DateTimeField(
            default=timezone.now,
            verbose_name=_('Bounce Date'))

    header = fields.TextField(
            blank=True,
            verbose_name=_('Header'))
    body = fields.TextField(
            blank=True,
            verbose_name=_('Body'))

    class Meta:
        abstract = True
        ordering = ['-date']
        verbose_name = _('Bounce')
        verbose_name_plural = _('Bounces')

    def save(self, **kwargs):
        if self.pk is None:
            if (self.domain_id is None
                    and self.subscriber_id is not None):
                self.domain_id = self.subscriber.email_domain_id
            if (self.newsletter_id is None
                    and self.message_id is not None):
                self.newsletter_id = self.message.newsletter_id
        super(AbstractBounce, self).save(**kwargs)


class AbstractClick(models.Model):

    link = models.ForeignKey(
            'MessageLink',
            editable=False,
            on_delete=models.CASCADE,
            related_name='clicks',
            verbose_name=_('Message Link'))
    message = models.ForeignKey(
            'Message',
            editable=False,
            on_delete=models.CASCADE,
            related_name='clicks',
            verbose_name=_('Message'))
    newsletter = models.ForeignKey(
            'Newsletter',
            editable=False,
            on_delete=models.CASCADE,
            related_name='clicks',
            verbose_name=_('Newsletter'))
    subscriber = models.ForeignKey(
            'Subscriber',
            editable=False,
            null=True,
            on_delete=models.SET_NULL,
            related_name='clicks',
            verbose_name=_('Subscriber'))
    domain = models.ForeignKey(
            'Domain',
            editable=False,
            null=True,
            on_delete=models.SET_NULL,
            related_name='clicks',
            verbose_name=_('E-mail Domain'))

    date = models.DateTimeField(
            auto_now_add=True,
            editable=False,
            verbose_name=_('Click Date'))

    class Meta:
        abstract = True
        ordering = ['-date']
        verbose_name = _('Click')
        verbose_name_plural = _('Clicks')

    def save(self, **kwargs):
        if self.pk is None:
            if (self.domain_id is None
                    and self.subscriber_id is not None):
                self.domain_id = self.subscriber.email_domain_id
            if (self.newsletter_id is None
                    and self.message_id is not None):
                self.newsletter_id = self.message.newsletter_id
        super(AbstractClick, self).save(**kwargs)


class AbstractDelivery(models.Model):

    message = models.ForeignKey(
            'Message',
            editable=False,
            on_delete=models.CASCADE,
            related_name='deliveries',
            verbose_name=_('Message'))
    newsletter = models.ForeignKey(
            'Newsletter',
            editable=False,
            on_delete=models.CASCADE,
            related_name='deliveries',
            verbose_name=_('Newsletter'))
    subscriber = models.ForeignKey(
            'Subscriber',
            editable=False,
            on_delete=models.CASCADE,
            related_name='deliveries',
            verbose_name=_('Subscriber'))
    domain = models.ForeignKey(
            'Domain',
            editable=False,
            on_delete=models.CASCADE,
            related_name='deliveries',
            verbose_name=_('E-mail Domain'))

    date = models.DateTimeField(
            db_index=True,
            editable=False,
            verbose_name=_('Estimated Date'))

    is_processed = fields.BooleanField(
            db_index=True,
            default=False,
            editable=False,
            verbose_name=_('Is Processed?'))
    process_date = models.DateTimeField(
            blank=True,
            editable=False,
            null=True,
            verbose_name=_('Effective Date'))
    is_bounced = fields.BooleanField(
            db_index=True,
            default=False,
            editable=False,
            verbose_name=_('Is Bounced?'))
    bounce_date = models.DateTimeField(
            blank=True,
            editable=False,
            null=True,
            verbose_name=_('Bounce Date'))
    is_opened = fields.BooleanField(
            db_index=True,
            default=False,
            editable=False,
            verbose_name=_('Is Opened?'))
    open_date = models.DateTimeField(
            blank=True,
            editable=False,
            null=True,
            verbose_name=_('Open Date'))
    is_clicked = fields.BooleanField(
            db_index=True,
            default=False,
            editable=False,
            verbose_name=_('Is Clicked?'))
    click_date = models.DateTimeField(
            blank=True,
            editable=False,
            null=True,
            verbose_name=_('Click Date'))

    class Meta:
        abstract = True
        ordering = ['-date']
        unique_together = [('message', 'subscriber')]
        verbose_name = _('Delivery')
        verbose_name_plural = _('Deliveries')

    def save(self, **kwargs):
        if self.pk is None:
            if (self.domain_id is None
                    and self.subscriber_id is not None):
                self.domain_id = self.subscriber.email_domain_id
            if (self.newsletter_id is None
                    and self.message_id is not None):
                self.newsletter_id = self.message.newsletter_id
        super(AbstractDelivery, self).save(**kwargs)

    # PROPERTIES

    @described_property(_('Response Time'))
    def response_time(self):
        if self.process_date is None or self.open_date is None:
            return None
        else:
            return self.open_date - self.process_date


@python_2_unicode_compatible
class AbstractDomain(models.Model):

    name = fields.CharField(
            editable=False,
            max_length=63,
            unique=True,
            validators=[RegexValidator(DOMAIN_RE)],
            verbose_name=_('Domain'))

    is_trusted = fields.BooleanField(
            default=False,
            verbose_name=_('Is Trusted?'))

    objects = models.Manager()
    cache = LookupTable(['name'])

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('E-mail Domain')
        verbose_name_plural = _('Domains')

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains', )


@python_2_unicode_compatible
class AbstractMessage(Logged, Slugged):

    newsletter = models.ForeignKey(
            'Newsletter',
            on_delete=models.CASCADE,
            related_name='messages',
            verbose_name=_('Newsletter'))

    guid = fields.GuidField(
            max_length=15,
            editable=False,
            unique=True,
            verbose_name=_('Global Unique Identifier'))

    subject = fields.CharField(
            max_length=255,
            verbose_name=_('Subject'))

    html = fields.TextField(
            verbose_name=_('HTML Version'))
    text = fields.TextField(
            blank=True,
            verbose_name=_('Plain Text Version'))

    is_sent = fields.BooleanField(
            default=False,
            editable=False,
            verbose_name=_('Is Sent?'))

    class Meta:
        abstract = True
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __str__(self):
        return self.subject

    @staticmethod
    def autocomplete_search_fields():
        return ('subject__icontains', )

    def get_absolute_url(self):
        kwargs = {
            #'message_pk': self.pk,
            #'message_slug': self.slug,
            'message_guid': self.guid,
        }
        return reverse('message', kwargs=kwargs)

    def save(self, **kwargs):
        if not self.text:
            self.text = extract_text(self.html)
        super(AbstractMessage, self).save(**kwargs)


@python_2_unicode_compatible
class AbstractMessageImage(Illustrated, Logged):

    guid = fields.GuidField(
            max_length=7,
            editable=False,
            unique=True,
            verbose_name=_('Global Unique Identifier'))

    name = fields.IdentifierField(
            unique=True,
            max_length=63,
            verbose_name=_('Name'))

    class Meta:
        abstract = True
        folder_name = 'newsletters'
        ordering = ['name']
        verbose_name = _('Message Image')
        verbose_name_plural = _('Message Images')

    def __str__(self):
        return self.name

    def get_upload_path(self, filename):
        return super(AbstractMessageImage, self).get_upload_path(self.name)


@python_2_unicode_compatible
class AbstractMessageLink(Logged):

    guid = fields.GuidField(
            max_length=15,
            editable=False,
            unique=True,
            verbose_name=_('Global Unique Identifier'))

    url = models.URLField(
            editable=True,
            unique=True,
            max_length=255,
            verbose_name=_('URL'))

    class Meta:
        abstract = True
        ordering = ['url']
        verbose_name = _('Message Link')
        verbose_name_plural = _('Message Links')

    def __str__(self):
        return self.url


@python_2_unicode_compatible
class AbstractNewsletter(Orderable, Logged, Slugged, MetaData):
    """
    A regularly distributed publication to which subscribers can subscribe.
    """

    connection = fields.CachedForeignKey(
            'emails.Connection',
            on_delete=models.CASCADE,
            related_name='newsletters',
            verbose_name=_('E-mail Connection'))

    guid = fields.GuidField(
            max_length=7,
            editable=False,
            unique=True,
            verbose_name=_('Global Unique Identifier'))

    name = fields.CharField(
            unique=True,
            max_length=63,
            verbose_name=_('Name'))
    description = fields.RichTextField(
            blank=True,
            verbose_name=_('Description'))
    is_published = fields.BooleanField(
            default=True,
            verbose_name=_('Is Published?'))

    sender_name = fields.CharField(
            max_length=127,
            verbose_name=_("Sender's Name"))
    sender_address = fields.CharField(
            max_length=127,
            verbose_name=_("Sender's Address"))
    reply_to_name = fields.CharField(
            blank=True,
            max_length=127,
            verbose_name=_("Reply To Name"))
    reply_to_address = fields.CharField(
            blank=True,
            max_length=127,
            verbose_name=_("Reply To Address"))
    return_path_name = fields.CharField(
            blank=True,
            max_length=127,
            verbose_name=_("Return To Name"))
    return_path_address = fields.CharField(
            blank=True,
            max_length=127,
            verbose_name=_("Return To Address"))

    objects = NewsletterManager()
    cache = LookupTable(['guid', 'name'])

    class Meta:
        abstract = True
        verbose_name = _('Newsletter')
        verbose_name_plural = _('Newsletters')

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains', )

    # CUSTOM METHODS

    def get_default_meta_index(self):
        if self.is_published:
            return super(AbstractNewsletter, self).get_default_meta_index()
        else:
            return False

    # PROPERTIES

    @described_property(_('Reply To'))
    def reply_to(self):
        if self.reply_to_name:
            return '"{0}" <{1}>'.format(self.reply_to_name, self.reply_to_address)
        elif self.reply_to_address:
            return self.reply_to_address
        else:
            return None

    @described_property(_('Return Path'))
    def return_path(self):
        if self.return_path_name:
            return '"{0}" <{1}>'.format(self.return_path_name, self.return_path_address)
        elif self.return_path_address:
            return self.return_path_address
        else:
            return None

    @described_property(_('Sender'))
    def sender(self):
        if self.sender_name:
            return '"{0}" <{1}>'.format(self.sender_name, self.sender_address)
        elif self.sender_address:
            return self.sender_address
        else:
            return None


class AbstractOpen(models.Model):

    message = models.ForeignKey(
            'Message',
            editable=False,
            on_delete=models.CASCADE,
            related_name='opens',
            verbose_name=_('Message'))
    newsletter = models.ForeignKey(
            'Newsletter',
            editable=False,
            on_delete=models.CASCADE,
            related_name='opens',
            verbose_name=_('Newsletter'))
    subscriber = models.ForeignKey(
            'Subscriber',
            editable=False,
            null=True,
            on_delete=models.SET_NULL,
            related_name='opens',
            verbose_name=_('Subscriber'))
    domain = models.ForeignKey(
            'Domain',
            editable=False,
            null=True,
            on_delete=models.SET_NULL,
            related_name='opens',
            verbose_name=_('E-mail Domain'))

    date = models.DateTimeField(
            auto_now_add=True,
            editable=False,
            verbose_name=_('Open Date'))

    class Meta:
        abstract = True
        ordering = ['-date']
        verbose_name = _('Open')
        verbose_name_plural = _('Opens')

    def save(self, **kwargs):
        if self.pk is None:
            if (self.domain_id is None
                    and self.subscriber_id is not None):
                self.domain_id = self.subscriber.email_domain_id
            if (self.newsletter_id is None
                    and self.message_id is not None):
                self.newsletter_id = self.message.newsletter_id
        super(AbstractOpen, self).save(**kwargs)


@python_2_unicode_compatible
class AbstractSubscriber(Enableable, Logged):

    guid = fields.GuidField(
            max_length=31,
            editable=False,
            unique=True,
            verbose_name=_('Global Unique Identifier'))

    email_address = fields.EmailField(
            max_length=127,
            unique=True,
            verbose_name=_('E-mail Address'))
    email_domain = models.ForeignKey(
            'Domain',
            editable=False,
            on_delete=models.CASCADE,
            related_name='subscribers',
            verbose_name=_('E-mail Domain'))
    first_name = fields.CharField(
            blank=True,
            max_length=63,
            verbose_name=_('First Name'))
    last_name = fields.CharField(
            blank=True,
            max_length=63,
            verbose_name=_('Last Name'))

    newsletters = models.ManyToManyField(
            'Newsletter',
            through='Subscription',
            related_name='subscribers',
            verbose_name=_('Newsletters'))
    tags = models.ManyToManyField(
            'SubscriberTag',
            blank=True,
            related_name='subscribers',
            verbose_name=_('Tags'))

    score = fields.FloatField(
            blank=True,
            db_index=True,
            default=2.0,
            editable=False,
            verbose_name=_('Score'))

    class Meta:
        abstract = True
        ordering = ['email_address']
        verbose_name = _('Subscriber')
        verbose_name_plural = _('Subscribers')

    def __str__(self):
        return self.email_address

    @staticmethod
    def autocomplete_search_fields():
        return ('email_address__icontains',
                'first_name__icontains',
                'last_name__icontains')

    # CUSTOM METHODS

    def is_subscribed_to(self, newsletter):
        if not self._get_pk_val():
            return False
        else:
            return self.subscriptions.filter(newsletter=newsletter).exists()

    def set_email(self, address):
        address = normalize_email(address)
        if not validate_email(address):
            msg = "'{0}' is not a valid email address."
            raise ValueError(msg.format(address))

        _, domain_name = address.rsplit('@', 1)
        domain, _ = Domain.objects.get_or_create(name=domain_name)

        self.email_address = address
        self.email_domain = domain

    def resubscribe_to(self, newsletter):
        if not self.is_subscribed_to(newsletter):
            qs = self.unsubscriptions.filter(newsletter=newsletter)
            unsubscription = qs.order_by('date').last()
            if unsubscription is not None:
                unsubscription.delete()
            return self.subscriptions.create(newsletter=newsletter)

    def subscribe_to(self, newsletter):
        if self.is_subscribed_to(newsletter):
            return None
        else:
            return self.subscriptions.create(newsletter=newsletter)

    def unsubscribe_from(self, newsletter, reason=None, last_message=None):
        if self.is_subscribed_to(newsletter):
            self.subscriptions.filter(newsletter=newsletter).delete()
            kwargs = {
                'newsletter': newsletter,
                'reason': reason,
                'last_message': last_message,
            }
            return self.unsubscriptions.create(**kwargs)

    # PROPERTIES

    @described_property(_('Name'))
    def full_name(self):
        return ' '.join((
            self.first_name,
            self.last_name,
        )).strip()


@python_2_unicode_compatible
class AbstractSubscriberTag(Logged):

    name = fields.CharField(
            unique=True,
            max_length=63,
            verbose_name=_('Name'))
    description = fields.TextField(
            blank=True,
            verbose_name=_('Description'))

    objects = models.Manager()
    cache = LookupTable(['name'])

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Subscriber Tag')
        verbose_name_plural = _('Subscriber Tags')

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains', )


class AbstractSubscription(models.Model):

    newsletter = models.ForeignKey(
            'Newsletter',
            editable=False,
            on_delete=models.CASCADE,
            related_name='subscriptions',
            verbose_name=_('Newsletter'))
    subscriber = models.ForeignKey(
            'Subscriber',
            editable=False,
            on_delete=models.CASCADE,
            related_name='subscriptions',
            verbose_name=_('Subscriber'))
    domain = models.ForeignKey(
            'Domain',
            editable=False,
            null=True,
            on_delete=models.SET_NULL,
            related_name='subscriptions',
            verbose_name=_('E-mail Domain'))

    date = models.DateTimeField(
            auto_now_add=True,
            editable=False,
            verbose_name=_('Subscription Date'))

    class Meta:
        abstract = True
        ordering = ['-date']
        unique_together = [('newsletter', 'subscriber')]
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')

    def save(self, **kwargs):
        if (self.pk is None
                and self.domain_id is None
                and self.subscriber_id is not None):
            self.domain_id = self.subscriber.email_domain_id
        super(AbstractSubscription, self).save(**kwargs)


class AbstractUnsubscription(models.Model):

    newsletter = models.ForeignKey(
            'Newsletter',
            editable=False,
            on_delete=models.CASCADE,
            related_name='unsubscriptions',
            verbose_name=_('Newsletter'))
    subscriber = models.ForeignKey(
            'Subscriber',
            editable=False,
            on_delete=models.CASCADE,
            related_name='unsubscriptions',
            verbose_name=_('Subscriber'))
    domain = models.ForeignKey(
            'Domain',
            editable=False,
            null=True,
            on_delete=models.SET_NULL,
            related_name='unsubscriptions',
            verbose_name=_('E-mail Domain'))

    date = models.DateTimeField(
            auto_now_add=True,
            editable=False,
            verbose_name=_('Unsubscribe Date'))
    reason = models.ForeignKey(
            'UnsubscriptionReason',
            editable=False,
            null=True,
            on_delete=models.CASCADE,
            related_name='unsubscriptions',
            verbose_name=_('Unsubscription Reason'))
    last_message = models.ForeignKey(
            'Message',
            editable=False,
            null=True,
            on_delete=models.CASCADE,
            related_name='unsubscriptions',
            verbose_name=_('Last Message'))

    class Meta:
        abstract = True
        ordering = ['-date']
        verbose_name = _('Unsubscription')
        verbose_name_plural = _('Unsubscriptions')

    def save(self, **kwargs):
        if self.pk is None:
            if (self.last_message_id is None
                    and self.newsletter_id is not None
                    and self.subscriber_id is not None):
                delivery = Delivery.objects.filter(
                    newsletter=self.newsletter_id,
                    subscriber=self.subscriber_id,
                ).order_by(
                    'date'
                ).last()
                if delivery is not None:
                    self.last_message_id = delivery.message_id

            if (self.domain_id is None
                    and self.subscriber_id is not None):
                self.domain_id = self.subscriber.email_domain_id

        super(AbstractUnsubscription, self).save(**kwargs)


@python_2_unicode_compatible
class AbstractUnsubscriptionReason(Orderable):

    description = fields.CharField(
            max_length=255,
            verbose_name=_('Description'))

    class Meta:
        abstract = True
        verbose_name = _('Unsubscription Reason')
        verbose_name_plural = _('Unsubscription Reasons')

    def __str__(self):
        return self.description

    @staticmethod
    def autocomplete_search_fields():
        return ('description__icontains', )

