# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.views import redirect_to_login
from django.utils.six.moves.urllib.parse import urlparse

from yepes.conf import settings


class LoginRequiredMiddleware(object):
    """
    Middleware that requires that users are authenticated for browse the site.

    Probably useful for sites that are on deploy or on testing.

    """
    def process_request(self, request):
        if request.user.is_anonymous():
            url = request.get_full_path()
            if urlparse(url).path != settings.LOGIN_URL:
                return redirect_to_login(url)

