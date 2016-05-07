# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import json
import time

from django import http
from django import test
from django.core.cache import caches, DEFAULT_CACHE_ALIAS
from django.core.exceptions import (
    ImproperlyConfigured,
    PermissionDenied,
    SuspiciousOperation,
)
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils import translation
from django.utils.encoding import force_text
from django.views.generic import FormView, View

from yepes.conf import settings
from yepes.view_mixins import (
    CacheMixin,
    CanonicalMixin,
    JsonMixin,
    MessageMixin,
    ModelMixin,
)

from .models import Article
from .forms import JsonMixinForm

@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
})
class CacheMixinTest(test.SimpleTestCase):

    def setUp(self):
        self.request_factory = test.RequestFactory()

    def tearDown(self):
        caches[DEFAULT_CACHE_ALIAS].clear()

    def assertResponseContentEqual(self, content, view, method, msg=None):
        req = getattr(self.request_factory, method)('/')
        resp = view(req)
        self.assertEqual(content, force_text(resp.content), msg=msg)

    def test_get_request(self):

        # WITHOUT CACHE MIXIN
        class TestView(View):
            iterator = iter('abcdef')
            def get(self, request, *args, **kwargs):
                return http.HttpResponse(next(self.iterator))

        view = TestView.as_view()
        self.assertResponseContentEqual('a', view, 'get')
        self.assertResponseContentEqual('b', view, 'get')
        self.assertResponseContentEqual('c', view, 'get')
        self.assertResponseContentEqual('d', view, 'get')
        self.assertResponseContentEqual('e', view, 'get')
        self.assertResponseContentEqual('f', view, 'get')

        # WITH CACHE MIXIN
        class TestView(CacheMixin, View):
            iterator = iter('abcdef')
            def get(self, request, *args, **kwargs):
                return http.HttpResponse(next(self.iterator))

        view = TestView.as_view()
        self.assertResponseContentEqual('a', view, 'get')
        self.assertResponseContentEqual('a', view, 'get')
        self.assertResponseContentEqual('a', view, 'get')
        self.assertResponseContentEqual('a', view, 'get')
        self.assertResponseContentEqual('a', view, 'get')
        self.assertResponseContentEqual('a', view, 'get')

    def test_post_request(self):

        # WITHOUT CACHE MIXIN
        class TestView(View):
            iterator = iter('abcdef')
            def post(self, request, *args, **kwargs):
                return http.HttpResponse(next(self.iterator))

        view = TestView.as_view()
        self.assertResponseContentEqual('a', view, 'post')
        self.assertResponseContentEqual('b', view, 'post')
        self.assertResponseContentEqual('c', view, 'post')
        self.assertResponseContentEqual('d', view, 'post')
        self.assertResponseContentEqual('e', view, 'post')
        self.assertResponseContentEqual('f', view, 'post')

        # WITH CACHE MIXIN
        class TestView(CacheMixin, View):
            iterator = iter('abcdef')
            def post(self, request, *args, **kwargs):
                return http.HttpResponse(next(self.iterator))

        view = TestView.as_view()
        self.assertResponseContentEqual('a', view, 'post')
        self.assertResponseContentEqual('b', view, 'post')
        self.assertResponseContentEqual('c', view, 'post')
        self.assertResponseContentEqual('d', view, 'post')
        self.assertResponseContentEqual('e', view, 'post')
        self.assertResponseContentEqual('f', view, 'post')

    def test_cache_expiration(self):

        class TestView(CacheMixin, View):
            delay = 0.2
            iterator = iter('abcdef')
            timeout = 0.4
            def get(self, request, *args, **kwargs):
                return http.HttpResponse(next(self.iterator))

        view = TestView.as_view()
        self.assertResponseContentEqual('a', view, 'get')
        self.assertResponseContentEqual('a', view, 'get')
        self.assertResponseContentEqual('a', view, 'get')
        self.assertResponseContentEqual('a', view, 'get')
        self.assertResponseContentEqual('a', view, 'get')
        self.assertResponseContentEqual('a', view, 'get')

        time.sleep(0.5)
        self.assertResponseContentEqual('b', view, 'get')
        self.assertResponseContentEqual('b', view, 'get')
        self.assertResponseContentEqual('b', view, 'get')
        self.assertResponseContentEqual('b', view, 'get')
        self.assertResponseContentEqual('b', view, 'get')
        self.assertResponseContentEqual('b', view, 'get')
        self.assertResponseContentEqual('b', view, 'get')

        time.sleep(1)
        self.assertResponseContentEqual('c', view, 'get')
        self.assertResponseContentEqual('c', view, 'get')
        self.assertResponseContentEqual('c', view, 'get')
        self.assertResponseContentEqual('c', view, 'get')
        self.assertResponseContentEqual('c', view, 'get')
        self.assertResponseContentEqual('c', view, 'get')


class CanonicalMixinTest(test.SimpleTestCase):

    def setUp(self):
        self.request_factory = test.RequestFactory()

    def test_redirection(self):
        title='Django for Dummies'
        slug='django-for-dummies'
        path = '/{0}.html'.format(slug)

        class TestView(CanonicalMixin, View):
            canonical_path = path
            def get(self, request, *args, **kwargs):
                return http.HttpResponse(title)

        view = TestView.as_view()
        resp = view(self.request_factory.get('/another-slug.html'))
        self.assertEqual(301, resp.status_code)
        self.assertEqual(path, resp['Location'])

        resp = view(self.request_factory.get(path))
        self.assertEqual(200, resp.status_code)
        self.assertEqual(title, force_text(resp.content))


class JsonMixinTest(test.SimpleTestCase):

    maxDiff = None

    def setUp(self):
        self.request_factory = test.RequestFactory()

    def test_success_response(self):
        data = {
            'foo': 'bar',
            'baz': 'qux',
            'quz': [{'foo': 'bar'}],
        }
        class TestView(JsonMixin, View):
            def get(self, response, *args, **kwargs):
                json = self.get_json_data(**data)
                return self.serialize_to_response(json)

        view = TestView.as_view()
        resp = view(self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        ))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            data,
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(200, resp.status_code)

    def test_method_not_allowed(self):
        class TestView(JsonMixin, View):
            pass

        view = TestView.as_view()
        resp = view(self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        ))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {'error': {'code': 405, 'message': 'Method not allowed'}},
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(405, resp.status_code)

    def test_not_found_exception(self):
        class TestView(JsonMixin, View):
            def get(self, response, *args, **kwargs):
                raise http.Http404('foo')

        view = TestView.as_view()
        resp = view(self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        ))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {'error': {'code': 404, 'message': 'foo'}},
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(404, resp.status_code)

    def test_not_found_response(self):
        class TestView(JsonMixin, View):
            def get(self, response, *args, **kwargs):
                return http.HttpResponseNotFound()

        view = TestView.as_view()
        resp = view(self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        ))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {'error': {'code': 404, 'message': 'Not found'}},
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(404, resp.status_code)

    def test_permission_denied_exception(self):
        class TestView(JsonMixin, View):
            def get(self, response, *args, **kwargs):
                raise PermissionDenied('bar')

        view = TestView.as_view()
        resp = view(self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        ))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {'error': {'code': 403, 'message': 'bar'}},
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(403, resp.status_code)

    def test_forbidden_response(self):
        class TestView(JsonMixin, View):
            def get(self, response, *args, **kwargs):
                return http.HttpResponseForbidden()

        view = TestView.as_view()
        resp = view(self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        ))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {'error': {'code': 403, 'message': 'Forbidden'}},
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(403, resp.status_code)

    def test_suspicious_operation_exception(self):
        class TestView(JsonMixin, View):
            def get(self, response, *args, **kwargs):
                raise SuspiciousOperation('baz')

        view = TestView.as_view()
        resp = view(self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        ))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {'error': {'code': 400, 'message': 'baz'}},
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(400, resp.status_code)

    def test_bad_request_response(self):
        class TestView(JsonMixin, View):
            def get(self, response, *args, **kwargs):
                return http.HttpResponseBadRequest()

        view = TestView.as_view()
        resp = view(self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        ))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {'error': {'code': 400, 'message': 'Bad request'}},
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(400, resp.status_code)

    def test_generic_exception(self):
        class TestView(JsonMixin, View):
            def get(self, response, *args, **kwargs):
                raise Exception('quz')

        view = TestView.as_view()
        resp = view(self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        ))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {'error': {'code': 500, 'message': 'quz'}},
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(500, resp.status_code)

    def test_server_error_response(self):
        class TestView(JsonMixin, View):
            def get(self, response, *args, **kwargs):
                return http.HttpResponseServerError()

        view = TestView.as_view()
        resp = view(self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        ))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {'error': {'code': 500, 'message': 'Internal server error'}},
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(500, resp.status_code)

    def test_redirect_response(self):
        class TestView(JsonMixin, View):
            def get(self, response, *args, **kwargs):
                return http.HttpResponseRedirect('baz')

        view = TestView.as_view()
        resp = view(self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        ))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {'error': {'code': 302, 'url': 'baz', 'message': 'Found'}},
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(302, resp.status_code)

    def test_permanent_redirect_response(self):
        class TestView(JsonMixin, View):
            def get(self, response, *args, **kwargs):
                return http.HttpResponsePermanentRedirect('baz')

        view = TestView.as_view()
        resp = view(self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        ))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {'error': {'code': 301, 'url': 'baz', 'message': 'Moved permanently'}},
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(301, resp.status_code)

    def test_system_exit_exception(self):
        class TestView(JsonMixin, View):
            def get(self, response, *args, **kwargs):
                raise SystemExit('qux')

        view = TestView.as_view()
        req = self.request_factory.get(
            '/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        with self.assertRaises(SystemExit):
            view(req)

    def test_override_content_type(self):
        mimetype = 'application/vnd.helloworld+json'
        data = {'foo': 'bar'}

        class TestView(JsonMixin, View):
            content_type = mimetype
            def get(self, response, *args, **kwargs):
                json = self.get_json_data(**data)
                return self.serialize_to_response(json)

        view = TestView.as_view()
        resp = view(self.request_factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest'))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(mimetype, resp['Content-Type'])
        self.assertEqual(data, json.loads(resp.content.decode('utf-8')))
        self.assertEqual(200, resp.status_code)

    def test_force_json_response(self):
        html_data = 'qux'
        json_data = {'foo': 'bar'}
        json_error = {'error': {'code': 501, 'message': 'Not implemented'}}

        class TestView(JsonMixin, View):
            force_json_response = False
            def get(self, response, *args, **kwargs):
                return http.HttpResponse(html_data)

        view = TestView.as_view()
        resp = view(self.request_factory.get('/'))
        self.assertIn('html', resp['Content-Type'])
        self.assertEqual(html_data, force_text(resp.content))
        self.assertEqual(200, resp.status_code)

        class TestView(JsonMixin, View):
            force_json_response = True
            def get(self, response, *args, **kwargs):
                return http.HttpResponse('qux')

        view = TestView.as_view()
        resp = view(self.request_factory.get('/'))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(json_error, json.loads(resp.content.decode('utf-8')))
        self.assertEqual(501, resp.status_code)

        class TestView(JsonMixin, View):
            force_json_response = False
            def get(self, response, *args, **kwargs):
                return http.HttpResponse(html_data)

        view = TestView.as_view()
        resp = view(self.request_factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest'))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(json_error, json.loads(resp.content.decode('utf-8')))
        self.assertEqual(501, resp.status_code)

        class TestView(JsonMixin, View):
            force_json_response = True
            def get(self, response, *args, **kwargs):
                return http.HttpResponse(html_data)

        view = TestView.as_view()
        resp = view(self.request_factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest'))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(json_error, json.loads(resp.content.decode('utf-8')))
        self.assertEqual(501, resp.status_code)

        class TestView(JsonMixin, View):
            force_json_response = False
            def get(self, response, *args, **kwargs):
                json = self.get_json_data(**json_data)
                return self.serialize_to_response(json)

        view = TestView.as_view()
        resp = view(self.request_factory.get('/'))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(json_data, json.loads(resp.content.decode('utf-8')))
        self.assertEqual(200, resp.status_code)

        class TestView(JsonMixin, View):
            force_json_response = True
            def get(self, response, *args, **kwargs):
                json = self.get_json_data(**json_data)
                return self.serialize_to_response(json)

        view = TestView.as_view()
        resp = view(self.request_factory.get('/'))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(json_data, json.loads(resp.content.decode('utf-8')))
        self.assertEqual(200, resp.status_code)

        class TestView(JsonMixin, View):
            force_json_response = False
            def get(self, response, *args, **kwargs):
                json = self.get_json_data(**json_data)
                return self.serialize_to_response(json)

        view = TestView.as_view()
        resp = view(self.request_factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest'))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(json_data, json.loads(resp.content.decode('utf-8')))
        self.assertEqual(200, resp.status_code)

        class TestView(JsonMixin, View):
            force_json_response = True
            def get(self, response, *args, **kwargs):
                json = self.get_json_data(**json_data)
                return self.serialize_to_response(json)

        view = TestView.as_view()
        resp = view(self.request_factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest'))
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(json_data, json.loads(resp.content.decode('utf-8')))
        self.assertEqual(200, resp.status_code)

    def test_form_views(self):

        class TestView(JsonMixin, FormView):
            form_class = JsonMixinForm
            success_url = 'baz'

        # VALID FORM
        view = TestView.as_view()
        resp = view(self.request_factory.post(
            '/',
            {'boolean': '1', 'char': 'quz', 'integer': '4'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'),
        )
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {'error': {'code': 302, 'url': 'baz', 'message': 'Found'}},
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(302, resp.status_code)

        # INVALID FORM
        resp = view(self.request_factory.post(
            '/',
            {'char': 'quzquzquz', 'integer': '444'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'),
        )
        self.assertIn('json', resp['Content-Type'])
        self.assertEqual(
            {
                'error': {'code': 484, 'message': 'Invalid form data'},
                'form_errors': {
                    'boolean': 'This field is required.',
                    'char': 'Ensure this value has at most 6 characters (it has 9).',
                    'integer': 'Ensure this value is less than or equal to 6.'},
            },
            json.loads(resp.content.decode('utf-8')),
        )
        self.assertEqual(484, resp.status_code)

        # LOCALIZED FORM ERRORS
        translation.activate('es')
        resp = view(self.request_factory.post(
            '/',
            {'char': 'quzquzquz', 'integer': '444'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'),
        )
        self.assertEqual(
            {
                'error': {'code': 484, 'message': 'Invalid form data'},
                'form_errors': {
                    'boolean': 'Este campo es obligatorio.',
                    'char': 'Asegúrese de que este valor tenga menos de 6 caracteres (tiene 9).',
                    'integer': 'Asegúrese de que este valor es menor o igual a 6.'},
            },
            json.loads(resp.content.decode('utf-8')),
        )
        translation.deactivate()


class DummyStorage(object):
    """
    Dummy message-store to test the message mixin.
    """
    def __init__(self):
        self.store = []

    def add(self, level, message, extra_tags=''):
        self.store.append(message)


class MessageMixinTest(test.SimpleTestCase):

    def setUp(self):
        self.storage = DummyStorage()
        self.request_factory = test.RequestFactory()
        self.request = self.request_factory.request()
        self.request._messages = self.storage

    def test_get_leave_message(self):
        class TestView(MessageMixin, View):
            pass
        self.assertFalse(TestView().get_leave_message(self.request))

        class TestView(MessageMixin, View):
            leave_message = False
        self.assertFalse(TestView().get_leave_message(self.request))

        class TestView(MessageMixin, View):
            leave_message = True
        self.assertTrue(TestView().get_leave_message(self.request))

    def test_get_success_message(self):
        class TestView(MessageMixin, View):
            pass
        with self.assertRaises(ImproperlyConfigured):
            TestView().get_success_message(self.request)

        class TestView(MessageMixin, View):
            success_message = None
        with self.assertRaises(ImproperlyConfigured):
            TestView().get_success_message(self.request)

        class TestView(MessageMixin, View):
            success_message = ''
        with self.assertRaises(ImproperlyConfigured):
            TestView().get_success_message(self.request)

        class TestView(MessageMixin, View):
            success_message = 'foo bar'
        self.assertEqual('foo bar', TestView().get_success_message(self.request))

    def test_send_success_message(self):
        class TestView(MessageMixin, View):
            pass
        TestView().send_success_message(self.request)
        self.assertEqual([], self.storage.store)

        class TestView(MessageMixin, View):
            leave_message = False
        TestView().send_success_message(self.request)
        self.assertEqual([], self.storage.store)

        class TestView(MessageMixin, View):
            leave_message = True
        with self.assertRaises(ImproperlyConfigured):
            TestView().send_success_message(self.request)

        class TestView(MessageMixin, View):
            leave_message = False
            success_message = 'foo bar'
        TestView().send_success_message(self.request)
        self.assertEqual([], self.storage.store)

        class TestView(MessageMixin, View):
            leave_message = True
            success_message = 'foo bar'
        TestView().send_success_message(self.request)
        self.assertEqual(['foo bar'], self.storage.store)


class ModelMixinTest(test.SimpleTestCase):

    def test_model_attribute(self):
        class TestView(ModelMixin, View):
            model = Article

        self.assertIs(Article, TestView().get_model())

    def test_object_attribute(self):
        class TestView(ModelMixin, View):
            def __init__(self, *args, **kwargs):
                super(TestView, self).__init__(*args, **kwargs)
                self.object = Article()

        self.assertIs(Article, TestView().get_model())

    def test_object_list_attribute(self):
        class TestView(ModelMixin, View):
            def __init__(self, *args, **kwargs):
                super(TestView, self).__init__(*args, **kwargs)
                self.object_list = Article.objects.all()

        self.assertIs(Article, TestView().get_model())

    def test_get_queryset_method(self):
        class TestView(ModelMixin, View):
            def get_queryset(self, *args, **kwargs):
                return Article.objects.all()

        self.assertIs(Article, TestView().get_model())

