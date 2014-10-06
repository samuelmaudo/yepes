# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.utils import translation

from yepes.conf import settings


class LocaleSubdomainsMiddleware(object):
    """
    Middleware that sets the language based on the request subdomain.
    """

    def process_request(self, request):
        """
        Adds a ``language`` attribute to the request object, which corresponds
        to the ``subdomain``, and activates the translation for this language.
        """
        supported_languages = dict(getattr(settings, 'LANGUAGES', ()))
        language = request.subdomain
        if language not in supported_languages:
            language = getattr(settings, 'LANGUAGE_CODE', 'en')

        translation.activate(language)
        request.language = translation.get_language()

    def process_response(self, request, response):
        """
        Ensures that the ``Content-Language`` is in the response.
        """
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()

        translation.deactivate()
        return response

