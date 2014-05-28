# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta
import re
import string
import time
import weakref

from django.contrib.sites.models import get_current_site
from django.db import transaction, IntegrityError
from django.db.models import F, Q
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.http import cookie_date
from django.utils.six.moves.urllib.parse import urlparse

from yepes.conf import settings
from yepes.apps.registry import registry
from yepes.loading import get_model
from yepes.types import Undefined
from yepes.utils.http import get_meta_data, urlunquote

Browser = get_model('metrics', 'Browser')
BrowserManager = Browser._default_manager
Country = get_model('standards', 'Country')
CountryManager = Country._default_manager
Engine = get_model('metrics', 'Engine')
EngineManager = Engine._default_manager
Language = get_model('standards', 'Language')
LanguageManager = Language._default_manager
Page = get_model('metrics', 'Page')
PageManager = Page._default_manager
PageView = get_model('metrics', 'PageView')
PageViewManager = PageView._default_manager
Platform = get_model('metrics', 'Platform')
PlatformManager = Platform._default_manager
Referrer = get_model('metrics', 'Referrer')
ReferrerManager = Referrer._default_manager
ReferrerPage = get_model('metrics', 'ReferrerPage')
ReferrerPageManager = ReferrerPage._default_manager
Region = get_model('standards', 'Region')
RegionManager = Region._default_manager
Visit = get_model('metrics', 'Visit')
VisitManager = Visit._default_manager
Visitor = get_model('metrics', 'Visitor')
VisitorManager = Visitor._default_manager

FAVICON_RE = re.compile(r'^/favicon[^/]*\.(ico|png)$')
SITEMAP_RE = re.compile(r'sitemap[^/]*\.xml$')
TEXT_FILES_RE = re.compile(r'[^/]+\.(txt|csv)$')
TOUCH_ICON_RE = re.compile(r'^/apple-touch-icon[^/]*\.png$')

LANGUAGE_RE = re.compile(r"""
    \b
    (?P<language>[a-z]{2,3})
    (?:-
        (?:
            (?P<country>[a-zA-Z]{2})
            |
            (?P<region>[0-9]{3})
        )
    )?
    \b
""", re.VERBOSE)

LOCALIZED_LANGUAGE_RE = re.compile(r"""
    \b
    (?P<language>[a-z]{2,3})
    -
    (?:
        (?P<country>[a-zA-Z]{2})
        |
        (?P<region>[0-9]{3})
    )
    \b
""", re.VERBOSE)


class MetricsProxy(object):

    _is_landing = Undefined
    _is_tracking = Undefined

    def __init__(self, middleware, request):
        self.request_date = timezone.now()
        self._middleware_ref = weakref.ref(middleware)
        self._request = request
        self._visitor_id = middleware.get_visitor_id(request)

    @property
    def _middleware(self):
        return self._middleware_ref()

    @property
    def is_landing(self):
        if self._is_landing is Undefined:
            if not self.is_tracking:
                self._is_landing = False
            elif not registry['metrics:RECORD_VISITORS']:
                self._is_landing = False
            elif self._visitor_id is None:
                self._is_landing = True
            else:
                visitor = VisitorManager.filter(key=self._visitor_id)
                self._is_landing = (not visitor.exists())

        return self._is_landing

    @property
    def is_tracking(self):
        if self._is_tracking is Undefined:
            self._is_tracking = self._middleware.must_track_request(
                    self._request,
                    get_meta_data(self._request, 'HTTP_USER_AGENT'),
                    get_current_site(self._request))

        return self._is_tracking

    @property
    def site_id(self):
        return getattr(settings, 'GOOGLE_ANALYTICS_ID', None)

    @property
    def visitor_id(self):
        if not self.is_tracking:
            return None
        elif not registry['metrics:RECORD_VISITORS']:
            return None
        elif self._visitor_id is None:
            self._is_landing = True
            self._visitor_id = self._middleware.generate_visitor_id(self._request)

        return self._visitor_id


class MetricsMiddleware(object):

    def process_request(self, request):
        request.metrics = MetricsProxy(self, request)

    def process_response(self, request, response):
        metrics = getattr(request, 'metrics', None)
        if metrics is None or not metrics.is_tracking:
            return response

        user_agent = get_meta_data(request, 'HTTP_USER_AGENT')
        current_site = get_current_site(request)
        args = (request, response, user_agent, current_site)

        if registry['metrics:RECORD_VISITORS']:

            try:
                visitor = VisitorManager.filter(
                    key=metrics.visitor_id,
                )[0]
            except IndexError:
                new_visitor = True
                visitor = Visitor()
                visitor.site = current_site
                visitor.key = metrics.visitor_id
                visitor.is_authenticated = self.is_visitor_authenticated(*args)
                visitor.save()
            else:
                new_visitor = False
                if (self.is_visitor_authenticated(*args)
                        and not visitor.is_authenticated):
                    visitor.is_authenticated = True
                    visitor.save(update_fields=['is_authenticated'])

            # This avoids the need to be calculated.
            metrics._is_landing = new_visitor

            if registry['metrics:RECORD_VISITS']:

                if new_visitor:
                    new_visit = True
                else:
                    timeout = timedelta(seconds=registry['metrics:VISIT_TIMEOUT'])
                    try:
                        visit = VisitManager.filter(
                            visitor=visitor,
                            end_date__gt=metrics.request_date - timeout,
                        )[0]
                    except IndexError:
                        new_visit = True
                    else:
                        new_visit = False
                        visit.end_date = metrics.request_date
                        visit.page_count = F('page_count') + 1
                        visit.save(update_fields=['end_date', 'page_count'])

                if new_visit:
                    visit = Visit()
                    visit.site = current_site
                    visit.visitor = visitor
                    visit.language_id = self.get_language(*args)
                    visit.country_id, visit.region_id = self.get_country(*args)
                    visit.browser_id = self.get_browser(*args)
                    visit.engine_id = self.get_engine(*args)
                    visit.platform_id = self.get_platform(*args)
                    visit.referrer_id, visit.referrer_page_id = self.get_referrer(*args)
                    visit.page_count = 1
                    visit.start_date = visit.end_date = metrics.request_date
                    visit.user_agent = user_agent[:255]
                    visit.save()

                if registry['metrics:RECORD_PAGE_VIEWS']:

                    current_page_id = self.get_page(*args)
                    previous_page_id = None
                    if not new_visit:
                        qs = PageViewManager.filter(visit=visit)
                        try:
                            previous_page_id = qs.values_list(
                                'page_id',
                                flat=True,
                            )[0]
                        except IndexError:
                            pass
                        else:
                            qs.update(next_page_id=current_page_id)

                    view = PageView()
                    view.visit = visit
                    view.page_id = current_page_id
                    view.previous_page_id = previous_page_id
                    view.status_code = response.status_code
                    view.date = metrics.request_date
                    view.load_time = (timezone.now() - view.date).total_seconds()
                    view.save()

                if self.must_send_cookie(*args):
                    response.set_cookie(
                            settings.METRICS_COOKIE_NAME,
                            metrics.visitor_id,
                            max_age=settings.SESSION_COOKIE_AGE,
                            expires=cookie_date(time.time() + settings.SESSION_COOKIE_AGE),
                            domain=settings.METRICS_COOKIE_DOMAIN,
                            path=settings.METRICS_COOKIE_PATH,
                            secure=settings.METRICS_COOKIE_SECURE or None,
                            httponly=settings.METRICS_COOKIE_HTTPONLY or None)

        return response

    # CUSTOM METHODS

    def generate_visitor_id(self, request):
        return get_random_string(32, string.ascii_letters + string.digits)

    def get_browser(self, request, response, user_agent, current_site):
        return BrowserManager.detect(user_agent)

    def get_country(self, request, response, user_agent, current_site):
        country_id, region_id = self.get_country_from_accept_language(
            get_meta_data(request, 'HTTP_ACCEPT_LANGUAGE')
        )
        if country_id or region_id:
            return (country_id, region_id)
        else:
            return self.get_country_from_user_agent(user_agent)

    def get_country_from_accept_language(self, accepted_languages):
        matchobj = LANGUAGE_RE.search(accepted_languages)
        if not matchobj:
            return (None, None)

        first_language = matchobj.group('language')
        country_id = None
        region_id = None
        for matchobj in LOCALIZED_LANGUAGE_RE.finditer(accepted_languages):
            if matchobj.group('language') == first_language:
                if matchobj.group('country'):
                    try:
                        country_id, region_id = CountryManager.filter(
                            code__iexact=matchobj.group('country'),
                        ).values_list(
                            'pk',
                            'region_id',
                        )[0]
                    except IndexError:
                        pass
                    else:
                        break
                else:
                    try:
                        region_id = RegionManager.filter(
                            number__iexact=matchobj.group('region'),
                        ).values_list(
                            'pk',
                            flat=True,
                        )[0]
                    except IndexError:
                        pass
                    else:
                        break

        return (country_id, region_id)

    def get_country_from_user_agent(self, user_agent):
        matchobj = LOCALIZED_LANGUAGE_RE.search(user_agent)
        if not matchobj:
            return (None, None)

        country_id = None
        region_id = None
        if matchobj.group('country'):
            try:
                country_id, region_id = CountryManager.filter(
                    code__iexact=matchobj.group('country'),
                ).values_list(
                    'pk',
                    'region_id',
                )[0]
            except IndexError:
                pass
        else:
            try:
                region_id = RegionManager.filter(
                    number__iexact=matchobj.group('region'),
                ).values_list(
                    'pk',
                    flat=True,
                )[0]
            except IndexError:
                pass

        return (country_id, region_id)

    def get_engine(self, request, response, user_agent, current_site):
        return EngineManager.detect(user_agent)

    def get_language(self, request, response, user_agent, current_site):
        language_id = self.get_language_from_accept_language(
            get_meta_data(request, 'HTTP_ACCEPT_LANGUAGE')
        )
        return language_id or self.get_language_from_user_agent(user_agent)

    def get_language_from_accept_language(self, accepted_languages):
        matchobj = LANGUAGE_RE.search(accepted_languages)
        if not matchobj:
            return None

        try:
            language_id = LanguageManager.filter(
                tag__iexact=matchobj.group('language'),
            ).values_list(
                'pk',
                flat=True,
            )[0]
        except IndexError:
            return None
        else:
            return language_id

    def get_language_from_user_agent(self, user_agent):
        matchobj = LOCALIZED_LANGUAGE_RE.search(user_agent)
        if not matchobj:
            return None

        try:
            language_id = LanguageManager.filter(
                tag__iexact=matchobj.group('language'),
            ).values_list(
                'pk',
                flat=True,
            )[0]
        except IndexError:
            return None
        else:
            return language_id

    def get_page(self, request, response, user_agent, current_site):
        parameters = []
        for key in sorted(request.GET):
            if key not in registry['metrics:EXCLUDED_PARAMETERS']:
                for value in request.GET.getlist(key):
                    parameters.append('{0}={1}'.format(key, value))
        query_string = '&'.join(parameters) if parameters else ''

        path = request.path
        if path.endswith('/'):
            path = path[:-1]
        if not path.startswith('/'):
            path = '/' + path
        i = path.rfind('/')
        path_head = path[:i]
        path_tail = path[i:]

        kwargs = {
            'site': current_site,
            'path_head': path_head[:255],
            'path_tail': path_tail[:63],
            'query_string': query_string[:255],
        }
        try:
            page_id = PageManager \
                .filter(**kwargs) \
                .values_list('pk', flat=True)[0]
        except IndexError:
            try:
                sid = transaction.savepoint()
                page = PageManager.create(**kwargs)
                page_id = page.pk
                transaction.savepoint_commit(sid)
            except IntegrityError:
                transaction.savepoint_rollback(sid)
                try:
                    page_id = PageManager \
                        .filter(**kwargs) \
                        .values_list('pk', flat=True)[0]
                except IndexError:
                    page_id = None

        return page_id

    def get_platform(self, request, response, user_agent, current_site):
        device_ua = (get_meta_data(request, 'HTTP_DEVICE_STOCK_UA')
                     or get_meta_data(request, 'HTTP_X_DEVICE_USER_AGENT')
                     or get_meta_data(request, 'HTTP_X_OPERAMINI_PHONE_UA')
                     or get_meta_data(request, 'HTTP_X_ORIGINAL_PHONE_UA')
                     or get_meta_data(request, 'HTTP_X_ORIGINAL_USER_AGENT')
                     or get_meta_data(request, 'HTTP_X_SKYFIRE_PHONE_UA')
                     or get_meta_data(request, 'HTTP_X_UCBROWSER_DEVICE_UA')
                     or user_agent)
        return PlatformManager.detect(device_ua)

    def get_referrer(self, request, response, user_agent, current_site):
        referrer_id = None
        referrer_page_id = None
        referrer_url = get_meta_data(request, 'HTTP_REFERER')

        ref = urlparse(referrer_url)
        if ref.geturl():

            cur_domain = current_site.domain
            if cur_domain.startswith('www.'):
                cur_domain = cur_domain[4:]
            if ':' in cur_domain:
                cur_domain = cur_domain[:cur_domain.find(':')]

            ref_domain = urlunquote(ref.hostname)
            if ref_domain.startswith('www.'):
                ref_domain = ref_domain[4:]

            ref_path = urlunquote(ref.path)
            if not ref_path.startswith('/'):
                ref_path = '/' + ref_path
            if ref.query:
                ref_path += '?' + urlunquote(ref.query)

            if ref_domain and cur_domain != ref_domain:
                kwargs = {
                    'domain': ref_domain[:63],
                }
                try:
                    referrer_id = ReferrerManager \
                        .filter(**kwargs) \
                        .values_list('pk', flat=True)[0]
                except IndexError:
                    try:
                        sid = transaction.savepoint()
                        referrer = ReferrerManager.create(**kwargs)
                        referrer_id = referrer.pk
                        transaction.savepoint_commit(sid)
                    except IntegrityError:
                        transaction.savepoint_rollback(sid)
                        try:
                            referrer_id = ReferrerManager \
                                .filter(**kwargs) \
                                .values_list('pk', flat=True)[0]
                        except IndexError:
                            pass

            if referrer_id:
                kwargs = {
                    'referrer_id': referrer_id,
                    'full_path': ref_path[:255],
                }
                try:
                    referrer_page_id = ReferrerPageManager \
                        .filter(**kwargs) \
                        .values_list('pk', flat=True)[0]
                except IndexError:
                    try:
                        sid = transaction.savepoint()
                        referrer_page = ReferrerPageManager.create(**kwargs)
                        referrer_page_id = referrer_page.pk
                        transaction.savepoint_commit(sid)
                    except IntegrityError:
                        transaction.savepoint_rollback(sid)
                        try:
                            referrer_page_id = ReferrerPageManager \
                                .filter(**kwargs) \
                                .values_list('pk', flat=True)[0]
                        except IndexError:
                            pass

        return (referrer_id, referrer_page_id)

    def get_visitor_id(self, request):
        return request.COOKIES.get(settings.METRICS_COOKIE_NAME)

    def is_visitor_authenticated(self, request, response, user_agent, current_site):
        return hasattr(request, 'user') and request.user.is_authenticated()

    def must_send_cookie(self, request, response, user_agent, current_site):
        return (not response.streaming
                and response.status_code < 500
                and response.get('Content-Type', '').startswith('text/html')
                and len(response.content) >= 200)

    def must_track_request(self, request, user_agent, current_site):
        if request.is_ajax():
            method = 'AJAX'
        else:
            method = get_meta_data(request, 'REQUEST_METHOD', 'GET').upper()
        if (method not in registry['metrics:TRACKED_REQUEST_METHODS']
                or not user_agent
                or FAVICON_RE.search(request.path)
                or SITEMAP_RE.search(request.path)
                or TEXT_FILES_RE.search(request.path)
                or TOUCH_ICON_RE.search(request.path)
                or hasattr(request, 'user') and request.user.is_staff):
            return False

        for path in registry['metrics:UNTRACKED_PATHS']:
            if request.path.startswith(path):
                return False

        referrer = get_meta_data(request, 'HTTP_REFERER').lower()
        for keyword in registry['metrics:UNTRACKED_REFERRERS']:
            if keyword.lower() in referrer:
                return False

        ua_lower = user_agent.lower()
        for keyword in registry['metrics:UNTRACKED_USER_AGENTS']:
            if keyword.lower() in ua_lower:
                return False

        return True


class LocatedMetricsMiddleware(MetricsMiddleware):

    # CUSTOM METHODS

    def get_country(self, request, response, user_agent, current_site):
        country_code = request.client_location.get('country_code')
        country_id = None
        region_id = None
        if country_code:
            try:
                country_id, region_id = CountryManager.filter(
                    code__iexact=country_code,
                ).values_list(
                    'pk',
                    'region_id',
                )[0]
            except IndexError:
                pass

        if country_id:
            return (country_id, region_id)
        else:
            return super(LocatedMetricsMiddleware, self).get_country(
                        request, response, user_agent, current_site)

