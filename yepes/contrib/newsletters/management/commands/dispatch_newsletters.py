# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from collections import namedtuple
from optparse import make_option

from django.core.mail import EmailMultiAlternatives
from django.core.management.base import NoArgsCommand
from django.utils import six
from django.utils import timezone

from yepes.apps import apps
from yepes.utils.minifier import minify_html

Delivery = apps.get_model('newsletters', 'Delivery')

prerender = apps.get_class('newsletters.utils', 'prerender')
render = apps.get_class('newsletters.utils', 'render')

PrerenderedMessage = namedtuple(
    'PrerenderedMessage',
    ['subject', 'text', 'html'],
)

class Command(NoArgsCommand):
    help = 'Processes pending deliveries.'
    option_list = NoArgsCommand.option_list + (
        make_option('-m', '--messages',
            action='store',
            default=100,
            dest='messages',
            help='Maximum number of messages that can be dispatched.',
            type='int'),
    )
    requires_model_validation = True

    def handle_noargs(self, **options):
        pending_deliveries = Delivery.objects.filter(
            is_processed=False,
            date__lte=timezone.now(),
        ).prefetch_related(
            'message',
            'newsletter',
            'subscriber',
        )[:options['messages']]

        if pending_deliveries:

            self.prerendered_messages = {}

            newsletters = {}
            for delivery in pending_deliveries:

                message = self.get_prerendered_message(delivery)
                context = {
                    'subscriber': delivery.subscriber,
                    'newsletter': delivery.newsletter,
                    'message': delivery.message,
                }
                name = delivery.subscriber.full_name
                address = delivery.subscriber.email_address
                if name:
                    recipient = '"{0}" <{1}>'.format(name, address)
                else:
                    recipient = address

                email = EmailMultiAlternatives(
                    message.subject,
                    render(message.text, context),
                    delivery.newsletter.sender,
                    [recipient],
                )
                email.attach_alternative(
                    render(message.html, context),
                    'text/html',
                )
                if delivery.newsletter.reply_to_address:
                    email.extra_headers['Reply-To'] = delivery.newsletter.reply_to

                if delivery.newsletter.return_path_address:
                    email.extra_headers['Return-Path'] = delivery.newsletter.return_path

                email.extra_headers['Precedence'] = 'bulk'

                if delivery.newsletter not in newsletters:
                    newsletters[delivery.newsletter] = [email]
                else:
                    newsletters[delivery.newsletter].append(email)

            for newsletter, emails in six.iteritems(newsletters):
                newsletter.connection.send_messages(emails)

            Delivery.objects.filter(
                pk__in=pending_deliveries,
            ).update(
                is_processed=True,
                process_date=timezone.now(),
            )
            self.stdout.write('Deliveries were successfully processed.')
        else:
            self.stdout.write('No pending deliveries.')

    def get_prerendered_message(self, delivery):
        msg = self.prerendered_messages.get(delivery.message.pk)
        if msg is None:
            context = {
                'subscriber': None, # Subscriber must not be specified here.
                'newsletter': delivery.newsletter,
                'message': delivery.message,
            }
            msg = PrerenderedMessage(
                delivery.message.subject,
                prerender(delivery.message.text, context),
                prerender(minify_html(delivery.message.html), context),
            )
            self.prerendered_messages[delivery.message.pk] = msg

        return msg

