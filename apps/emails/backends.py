# -*- coding:utf-8 -*-

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend as SmtpBackend

from yepes.loading import get_model

Delivery = get_model('emails', 'Delivery')

__all__ = ('LoggedSmtpBackend', 'SmtpBackend')


class LoggedSmtpBackend(SmtpBackend):
    """
    Inherits from ``smtp`` backend but stores one copy of each dispatched
    message in the database.
    """

    def _send(self, message):
        """
        Sends the email message and keeps a copy in the database if no errors.
        """
        if super(LoggedSmtpBackend, self)._send(message):
            delivery = Delivery()
            delivery.subject = message.subject
            delivery.sender = message.from_email
            delivery.recipients = ', '.join(message.to)
            delivery.other_recipients = ', '.join(message.cc)
            delivery.hidden_recipients = ', '.join(message.bcc)

            if isinstance(message, EmailMultiAlternatives):
                for content, mimetype in message.alternatives:
                    if mimetype == 'text/html':
                        delivery.html = content
                    elif mimetype == 'text/plain':
                        delivery.text = content

            if message.content_subtype == 'html':
                delivery.html = message.body
            elif message.content_subtype == 'plain':
                delivery.text = message.body

            delivery.save()
            return True
        else:
            return False

