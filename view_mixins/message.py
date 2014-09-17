# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages


class MessageMixin(object):

    leave_message = False
    success_message = None

    def get_leave_message(self, request):
        return self.leave_message

    def get_success_message(self, request):
        if self.success_message:
            return self.success_message
        else:
            msg = "No message to leave. Provide a ``success_message``."
            raise ImproperlyConfigured(msg)

    def send_success_message(self, request):
        if self.get_leave_message(request):
            msg = self.get_success_message(request)
            messages.success(request, msg)

