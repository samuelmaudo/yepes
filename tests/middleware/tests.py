# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django import test
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpRequest, HttpResponse
from django.template import RequestContext, Template
from django.template.context_processors import csrf
from django.test.utils import override_settings
from django.utils import translation
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import (
    csrf_exempt,
    requires_csrf_token,
    ensure_csrf_cookie,
)

from yepes.conf import settings
from yepes.contrib.registry import registry
from yepes.middleware.client_ip import ClientIpMiddleware
from yepes.middleware.csrf_token import CsrfTokenMiddleware
from yepes.middleware.html_minifier import HtmlMinifierMiddleware
from yepes.middleware.locale_subdomains import LocaleSubdomainsMiddleware
from yepes.middleware.login_required import LoginRequiredMiddleware
from yepes.middleware.phased_render import PhasedRenderMiddleware
from yepes.middleware.ssl_redirect import SSLRedirectMiddleware
from yepes.middleware.subdomains import SubdomainsMiddleware
from yepes.test.decorators import override_registry
from yepes.utils import phased


def token_view(request):
    """
    A view that uses {% csrf_token %}.
    """
    context = RequestContext(request)
    template = Template('{% csrf_token %}')
    return HttpResponse(template.render(context))


def non_token_view_using_request_processor(request):
    """
    A view that doesn't use the token, but does use the csrf view processor.
    """
    context = RequestContext(request, processors=[csrf])
    template = Template('')
    return HttpResponse(template.render(context))


class ClientIpMiddlewareTest(test.TestCase):

    def setUp(self):
        self.middleware = ClientIpMiddleware()

    def test_default_ip(self):
        request = HttpRequest()
        self.middleware.process_request(request)
        self.assertEqual(request.client_ip, '127.0.0.1')

    def test_forwarded_for(self):
        request = HttpRequest()
        request.META = {'HTTP_X_FORWARDED_FOR': '255.0.0.25'}
        self.middleware.process_request(request)
        self.assertEqual(request.client_ip, '255.0.0.25')

        request = HttpRequest()
        request.META = {'HTTP_X_FORWARDED_FOR': '255.0.0.25, 122.0.0.12'}
        self.middleware.process_request(request)
        self.assertEqual(request.client_ip, '255.0.0.25')

        request = HttpRequest()
        request.META = {
            'HTTP_X_FORWARDED_FOR': '255.0.0.25',
            'HTTP_X_REAL_IP': '122.0.0.12',
            'REMOTE_ADDR': '127.0.0.1',
        }
        self.middleware.process_request(request)
        self.assertEqual(request.client_ip, '255.0.0.25')

    def test_real_ip(self):
        request = HttpRequest()
        request.META = {'HTTP_X_REAL_IP': '255.0.0.25'}
        self.middleware.process_request(request)
        self.assertEqual(request.client_ip, '255.0.0.25')

        request = HttpRequest()
        request.META = {'HTTP_X_REAL_IP': '255.0.0.25, 122.0.0.12'}
        self.middleware.process_request(request)
        self.assertEqual(request.client_ip, '255.0.0.25')

        request = HttpRequest()
        request.META = {
            'HTTP_X_REAL_IP': '255.0.0.25',
            'REMOTE_ADDR': '122.0.0.12',
        }
        self.middleware.process_request(request)
        self.assertEqual(request.client_ip, '255.0.0.25')

    def test_remote_addr(self):
        request = HttpRequest()
        request.META = {'REMOTE_ADDR': '255.0.0.25'}
        self.middleware.process_request(request)
        self.assertEqual(request.client_ip, '255.0.0.25')

        request = HttpRequest()
        request.META = {'REMOTE_ADDR': '255.0.0.25, 122.0.0.12'}
        self.middleware.process_request(request)
        self.assertEqual(request.client_ip, '255.0.0.25')

    @override_registry({'core:BANNED_IP_ADDRESSES': ('255.0.0.25', )})
    def test_banned_ip(self):
        request = HttpRequest()
        request.META = {'HTTP_X_FORWARDED_FOR': '255.0.0.25'}
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 403)

        request = HttpRequest()
        request.META = {'HTTP_X_FORWARDED_FOR': '122.0.0.12'}
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

        request = HttpRequest()
        request.META = {'HTTP_X_REAL_IP': '255.0.0.25'}
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 403)

        request = HttpRequest()
        request.META = {'HTTP_X_REAL_IP': '122.0.0.12'}
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

        request = HttpRequest()
        request.META = {'REMOTE_ADDR': '255.0.0.25'}
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 403)

        request = HttpRequest()
        request.META = {'REMOTE_ADDR': '122.0.0.12'}
        response = self.middleware.process_request(request)
        self.assertIsNone(response)


class CsrfTokenMiddlewareTest(test.SimpleTestCase):

    def setUp(self):
        self.middleware = CsrfTokenMiddleware()

    @override_settings(
        CSRF_COOKIE_NAME='myname',
        CSRF_COOKIE_DOMAIN='.example.com',
        CSRF_COOKIE_PATH='/test/',
        CSRF_COOKIE_SECURE=True,
        CSRF_COOKIE_HTTPONLY=True,
    )
    def test_process_response_get_token_used(self):
        """
        When ``get_token()`` is used, check that the cookie is created and
        headers patched.
        """
        request = HttpRequest()

        # token_view calls get_token() indirectly
        self.middleware.process_view(request, token_view, (), {})
        response = token_view(request)
        response_2 = self.middleware.process_response(request, response)

        csrf_cookie = response_2.cookies.get('myname', False)
        self.assertNotEqual(csrf_cookie, False)
        self.assertEqual(csrf_cookie['domain'], '.example.com')
        self.assertEqual(csrf_cookie['secure'], True)
        self.assertEqual(csrf_cookie['httponly'], True)
        self.assertEqual(csrf_cookie['path'], '/test/')
        self.assertIn('Cookie', response_2.get('Vary',''))

    def test_process_response_get_token_not_used(self):
        """
        Check that if ``get_token()`` is not called, the view middleware
        does not add a cookie.
        """
        # This is important to make pages cacheable. Pages which do call
        # get_token(), assuming they use the token, are not cacheable because
        # the token is specific to the user
        request = HttpRequest()
        # non_token_view_using_request_processor does not call get_token(), but
        # does use the csrf request processor. By using this, we are testing
        # that the view processor is properly lazy and doesn't call get_token()
        # until needed.
        self.middleware.process_view(request, non_token_view_using_request_processor, (), {})
        response = non_token_view_using_request_processor(request)
        response_2 = self.middleware.process_response(request, response)

        csrf_cookie = response_2.cookies.get(settings.CSRF_COOKIE_NAME, False)
        self.assertEqual(csrf_cookie, False)

    def test_ensures_csrf_cookie_with_middleware(self):
        """
        Tests that ``ensures_csrf_cookie`` decorator fulfils its promise with
        the middleware enabled.
        """
        @ensure_csrf_cookie
        def view(request):
            # Doesn't insert a token or anything
            return HttpResponse(content='')

        request = HttpRequest()
        self.middleware.process_view(request, view, (), {})
        response = view(request)
        response_2 = self.middleware.process_response(request, response)
        self.assertIn(settings.CSRF_COOKIE_NAME, response_2.cookies)
        self.assertIn('Cookie', response_2.get('Vary',''))


class HtmlMinifierMiddlewareTest(test.SimpleTestCase):

    html_code = (
        '<!DOCTYPE html>\n'
        '<html>\n'
        '  <head>\n'
        '    <title>This is a title</title>\n'
        '    <!--This is a comment.-->\n'
        '    <!--[if IE]>This is a conditional comment<![endif]-->\n'
        '  </head>\n'
        '  <body>\n'
        '\n'
        '    <p>This is a paragraph.</p>\n'
        '    \n'
        '    <!-- This is another comment. -->\n'
        '\n'
        '  </body>\n'
        '</html>\n'
    )
    minified_html_code = (
        '<!DOCTYPE html>\n'
        '<html>\n'
        '<head>\n'
        '<title>This is a title</title>\n'
        '<!--[if IE]>This is a conditional comment<![endif]-->\n'
        '</head>\n'
        '<body>\n'
        '<p>This is a paragraph.</p>\n'
        '</body>\n'
        '</html>\n'
    )
    def setUp(self):
        self.middleware = HtmlMinifierMiddleware()

    def test_html(self):
        request = HttpRequest()
        response = HttpResponse(self.html_code)
        response_2 = self.middleware.process_response(request, response)
        self.assertEqual(response_2.content, force_bytes(self.minified_html_code))

    def test_not_html(self):
        request = HttpRequest()
        response = HttpResponse(self.html_code, content_type='application/json')
        response_2 = self.middleware.process_response(request, response)
        self.assertEqual(response_2.content, force_bytes(self.html_code))


class LocaleSubdomainsMiddlewareTest(test.SimpleTestCase):

    def setUp(self):
        self.middleware = LocaleSubdomainsMiddleware()

    def test_supported_translation(self):
        default_language = translation.get_language()
        request = HttpRequest()
        request.subdomain = 'fr' if 'fr' != default_language else 'zh'
        self.middleware.process_request(request)
        self.assertEqual(translation.get_language(), request.subdomain)
        response = HttpResponse()
        self.middleware.process_response(request, response)
        self.assertEqual(translation.get_language(), default_language)

    @override_settings(LANGUAGES=('it', ))
    def test_fallback_translation(self):
        default_language = translation.get_language()
        request = HttpRequest()
        request.subdomain = 'fr' if 'fr' != default_language else 'zh'
        self.middleware.process_request(request)
        self.assertEqual(translation.get_language(), 'en')
        response = HttpResponse()
        self.middleware.process_response(request, response)
        self.assertEqual(translation.get_language(), default_language)


class LoginRequiredMiddlewareTest(test.SimpleTestCase):

    def setUp(self):
        self.middleware = LoginRequiredMiddleware()

    def test_anonymous_user(self):
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
        }
        request.path = request.path_info = '/'
        request.user = AnonymousUser()
        response = self.middleware.process_request(request)
        self.assertIn('Location', response)
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user(self):
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
        }
        request.path = request.path_info = '/'
        request.user = User()
        response = self.middleware.process_request(request)
        self.assertIsNone(response)


class PhasedRenderMiddlewareTestCase(test.SimpleTestCase):

    template = (
        'before '
        '{delimiter}'
        'inside{{# a comment #}} '
        '{delimiter}'
        'after'
    )
    first_render = template.format(delimiter=phased.SECRET_DELIMITER)
    second_render = 'before inside after'

    def setUp(self):
        self.middleware = PhasedRenderMiddleware()

    def test_html(self):
        request = HttpRequest()
        response = HttpResponse(self.first_render)
        response_2 = self.middleware.process_response(request, response)
        self.assertEqual(response_2.content, force_bytes(self.second_render))

    def test_not_html(self):
        request = HttpRequest()
        response = HttpResponse(self.first_render, content_type='application/json')
        response_2 = self.middleware.process_response(request, response)
        self.assertEqual(response_2.content, force_bytes(self.first_render))


class SSLRedirectMiddlewareTest(test.SimpleTestCase):

    def setUp(self):
        self.middleware = SSLRedirectMiddleware()

    @override_settings(SSL_ENABLED=True, SSL_PATHS=('/admin', ))
    def test_ssl_enabled(self):
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
        }
        request.path = request.path_info = '/'
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
        }
        request.path = request.path_info = '/admin/'
        response = self.middleware.process_request(request)
        self.assertEqual(response['Location'], 'https://example.com/admin/')
        self.assertEqual(response.status_code, 301)

        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
            'HTTP_X_FORWARDED_SSL': 'on',
        }
        request.path = request.path_info = '/'
        response = self.middleware.process_request(request)
        self.assertEqual(response['Location'], 'http://example.com/')
        self.assertEqual(response.status_code, 301)

        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
            'HTTP_X_FORWARDED_SSL': 'on',
        }
        request.path = request.path_info = '/admin/'
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
            'HTTP_X_FORWARDED_PROTO': 'https',
        }
        request.path = request.path_info = '/admin/'
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
            'HTTP_X_FORWARDED_HOST': 'example.com:443',
        }
        request.path = request.path_info = '/admin/'
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    @override_settings(SSL_ENABLED=False, SSL_PATHS=('/admin', ))
    def test_ssl_disabled(self):
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
        }
        request.path = request.path_info = '/'
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
        }
        request.path = request.path_info = '/admin/'
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
            'HTTP_X_FORWARDED_SSL': 'on',
        }
        request.path = request.path_info = '/'
        response = self.middleware.process_request(request)
        self.assertEqual(response['Location'], 'http://example.com/')
        self.assertEqual(response.status_code, 301)

        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
            'HTTP_X_FORWARDED_SSL': 'on',
        }
        request.path = request.path_info = '/admin/'
        response = self.middleware.process_request(request)
        self.assertEqual(response['Location'], 'http://example.com/admin/')
        self.assertEqual(response.status_code, 301)

        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
            'HTTP_X_FORWARDED_PROTO': 'https',
        }
        request.path = request.path_info = '/admin/'
        response = self.middleware.process_request(request)
        self.assertEqual(response['Location'], 'http://example.com/admin/')
        self.assertEqual(response.status_code, 301)

        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'example.com',
            'SERVER_PORT': '80',
            'HTTP_X_FORWARDED_HOST': 'example.com:443',
        }
        request.path = request.path_info = '/admin/'
        response = self.middleware.process_request(request)
        self.assertEqual(response['Location'], 'http://example.com/admin/')
        self.assertEqual(response.status_code, 301)



class SubdomainsMiddlewareTest(test.TestCase):

    def setUp(self):
        self.middleware = SubdomainsMiddleware()

    def test_simple_subdomain(self):
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'm.example.com',
            'SERVER_PORT': '80',
        }
        request.path = request.path_info = '/'
        self.middleware.process_request(request)
        self.assertEqual(request.subdomain, 'm')

    def test_complex_subdomain(self):
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'touch.www.example.com',
            'SERVER_PORT': '80',
        }
        request.path = request.path_info = '/'
        self.middleware.process_request(request)
        self.assertEqual(request.subdomain, 'touch.www')

    def test_invalid_host(self):
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'm.example.org',
            'SERVER_PORT': '80',
        }
        request.path = request.path_info = '/'
        self.middleware.process_request(request)
        self.assertEqual(request.subdomain, '')

    @override_registry({'core:ALLOWED_SUBDOMAINS': ('m', )})
    def test_allowed_subdomain(self):
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'm.example.com',
            'SERVER_PORT': '80',
        }
        request.path = request.path_info = '/'
        self.middleware.process_request(request)
        self.assertEqual(request.subdomain, 'm')

    @override_registry({'core:ALLOWED_SUBDOMAINS': ('m', )})
    def test_disallowed_subdomain(self):
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'touch.www.example.com',
            'SERVER_PORT': '80',
        }
        request.path = request.path_info = '/'
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, 404)

