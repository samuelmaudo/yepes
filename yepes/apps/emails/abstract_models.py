# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template import Context, Template
from django.utils.encoding import python_2_unicode_compatible
from django.utils.formats import date_format
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.cache import LookupTable
from yepes.loading import get_model
from yepes.model_mixins import Logged
from yepes.utils.html import extract_text
from yepes.utils.properties import described_property


@python_2_unicode_compatible
class AbstractConnection(Logged):

    name = fields.CharField(
            max_length=63,
            unique=True,
            verbose_name=_('Name'))

    host = fields.CharField(
            max_length=255,
            verbose_name=_('Host'),
            help_text = _('Address of the SMTP server.'))
    port = fields.IntegerField(
            default=25,
            min_value=0,
            verbose_name=_('Port'))
    username = fields.CharField(
            max_length=255,
            verbose_name=_('Username'))
    password = fields.EncryptedCharField(
            max_length=255,
            verbose_name=_('Password'))

    is_secure = fields.BooleanField(
            default=False,
            verbose_name=_('Use TLS?'),
            help_text=_('Whether to use a secure connection when talking to the SMTP server.'))
    is_logged = fields.BooleanField(
            default=False,
            verbose_name=_('Store Mails?'),
            help_text=_('Whether to store a copy of each sent mail.'))

    cache = LookupTable()

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('E-mail Connection')
        verbose_name_plural = _('Connections')

    _connection = None

    def __str__(self):
        return '{0} ({1})'.format(self.name, self.host)

    def save(self, **kwargs):
        """
        Saves the record back to the database. Take into account that this
        closes the network connection if it was open.
        """
        self.close()
        self._connection = None
        super(AbstractConnection, self).save(**kwargs)

    # CUSTOM METHODS

    def close(self):
        """
        Closes the connection to the email server.
        """
        if self._connection is not None:
            self._connection.close()

    def open(self):
        """
        Ensures we have a connection to the email server. Returns whether or
        not a new connection was required (True or False).
        """
        return self.smtp_connection.open()

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        return self.smtp_connection.send_messages(email_messages)

    # PROPERTIES

    @property
    def smtp_connection(self):
        """
        Returns an instance of the SMTP email backend. This instance uses the
        authentication credentials set in the record to connect the SMTP server.
        """
        if self._connection is None:
            if self.is_logged:
                backend = 'yepes.apps.emails.backends.LoggedSmtpBackend'
            else:
                backend = 'yepes.apps.emails.backends.SmtpBackend'

            self._connection = mail.get_connection(
                backend, **{
                'host': self.host,
                'port': self.port,
                'username': self.username,
                'password': self.password,
                'use_tls': self.is_secure,
            })
        return self._connection

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('host__icontains', )


@python_2_unicode_compatible
class AbstractDelivery(models.Model):

    date = models.DateTimeField(
            auto_now_add=True,
            verbose_name=_('Date'))

    sender = fields.CharField(
            max_length=255,
            verbose_name=_('Sender'))
    recipients = fields.TextField(
            blank=True,
            verbose_name=_('Recipients'))
    other_recipients = fields.TextField(
            blank=True,
            verbose_name=_('Other Recipients'))
    hidden_recipients = fields.TextField(
            blank=True,
            verbose_name=_('Hidden Recipients'))

    subject = fields.CharField(
            blank=True,
            max_length=255,
            verbose_name=_('Subject'))

    html = fields.TextField(
            blank=True,
            verbose_name=_('HTML Version'))
    text = fields.TextField(
            blank=True,
            verbose_name=_('Plain Text Version'))

    class Meta:
        abstract = True
        ordering = ['-date']
        verbose_name = _('Delivery')
        verbose_name_plural = _('Deliveries')

    def __str__(self):
        args = (
            self.subject or ugettext('No subject'),
            date_format(self.date, 'SHORT_DATE_FORMAT'),
        )
        return '{0} ({1})'.format(*args)


@python_2_unicode_compatible
class AbstractMessage(Logged):

    connection = fields.CachedForeignKey(
            'Connection',
            related_name='messages',
            verbose_name=_('Connection'))

    name = fields.CharField(
            unique=True,
            max_length=63,
            verbose_name=_('Name'))

    sender_name = fields.CharField(
            max_length=127,
            verbose_name=_("Sender's Name"))
    sender_address = fields.CharField(
            max_length=127,
            verbose_name=_("Sender's Address"))
    recipient_name = fields.CharField(
            blank=True,
            max_length=255,
            verbose_name=_("Recipient's Name"))
    recipient_address = fields.CharField(
            blank=True,
            max_length=255,
            verbose_name=_("Recipient's Address"),
            help_text=_('If field is blank, it will be populated when the message is sent.'))
    reply_to_name = fields.CharField(
            blank=True,
            max_length=127,
            verbose_name=_("Reply To Name"))
    reply_to_address = fields.CharField(
            blank=True,
            max_length=127,
            verbose_name=_("Reply To Address"))

    subject = fields.CharField(
            max_length=255,
            verbose_name=_('Subject'))

    html = fields.TextField(
            verbose_name=_('HTML Version'))
    text = fields.TextField(
            blank=True,
            verbose_name=_('Plain Text Version'))

    class Meta:
        abstract = True
        ordering = ['name']
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.text:
            self.text = extract_text(self.html)
        super(AbstractMessage, self).save(**kwargs)

    # CUSTOM METHODS

    def render(self, context=None):
        if not isinstance(context, Context):
            context = Context(context)

        email = EmailMultiAlternatives(
            Template(self.subject).render(context),
            Template(self.text).render(context),
            self.sender,
            self.recipient,
            connection=self.connection,
        )
        email.attach_alternative(
            Template(self.html).render(context),
            'text/html',
        )
        if self.reply_to_address:
            email.extra_headers['Reply-To'] = self.reply_to

        return email

    def render_and_send(self, recipient_list, reply_to=None, context=None,
                        connection=None):
        to = []
        for recipient in recipient_list:
            if isinstance(recipient, (tuple, list)):
                name = recipient[0].strip()
                address = recipient[1].strip()
                if name:
                    to.append('"{0}" <{1}>'.format(name, address))
                else:
                    to.append(address)
            else:
                to.append(recipient)

        if isinstance(reply_to, (tuple, list)):
            name = reply_to[0].strip()
            address = reply_to[1].strip()
            if name:
                reply_to = '"{0}" <{1}>'.format(name, address)
            else:
                reply_to = address

        email = self.render(context)
        if not email.to:
            email.to = to
        if 'Reply-To' not in email.extra_headers and reply_to:
            email.extra_headers['Reply-To'] = reply_to
        if connection is not None:
            email.connection = connection
        email.send()

    # PROPERTIES

    @described_property(_('Recipient'), cached=True)
    def recipient(self):
        recipient_list = []
        if self.recipient_address.strip():
            name_list= self.recipient_name.split(',')
            address_list = self.recipient_address.split(',')
            for i, address in enumerate(address_list):
                address = address.strip()
                if len(name_list) > i:
                    name = name_list[i].strip()
                    recipient_list.append('"{0}" <{1}>'.format(name, address))
                else:
                    recipient_list.append(address)

        return recipient_list

    @described_property(_('Reply To'), cached=True)
    def reply_to(self):
        if self.reply_to_name:
            return '"{0}" <{1}>'.format(self.reply_to_name, self.reply_to_address)
        elif self.reply_to_address:
            return self.reply_to_address
        else:
            return None

    @described_property(_('Sender'), cached=True)
    def sender(self):
        if self.sender_name:
            return '"{0}" <{1}>'.format(self.sender_name, self.sender_address)
        elif self.sender_address:
            return self.sender_address
        else:
            return None

    # GRAPPELLI SETTINGS

    @staticmethod
    def autocomplete_search_fields():
        return ('name__icontains', 'subject__icontains')

