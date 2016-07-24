# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.formats import date_format
from django.utils.translation import ugettext_lazy as _

from yepes import fields
from yepes.apps import apps
from yepes.loading import LazyModel
from yepes.types import Undefined

Page = LazyModel('metrics', 'Page')
Parameter = apps.get_class('metrics.model_mixins', 'Parameter')

CountryField = apps.get_class('standards.fields', 'CountryField')
LanguageField = apps.get_class('standards.fields', 'LanguageField')
RegionField = apps.get_class('standards.fields', 'RegionField')


class AbstractBrowser(Parameter):

    class Meta:
        abstract = True
        ordering = ['index']
        verbose_name = _('Browser')
        verbose_name_plural = _('Browsers')


class AbstractEngine(Parameter):

    class Meta:
        abstract = True
        ordering = ['index']
        verbose_name = _('Rendering Engine')
        verbose_name_plural = _('Rendering Engines')


class AbstractPlatform(Parameter):

    class Meta:
        abstract = True
        ordering = ['index']
        verbose_name = _('Platform')
        verbose_name_plural = _('Platforms')


@python_2_unicode_compatible
class AbstractPage(models.Model):

    site = models.ForeignKey(
            'sites.Site',
            on_delete=models.CASCADE,
            related_name='pages',
            verbose_name=_('Site'))
    path_head = fields.CharField(
            blank=True,
            max_length=255,
            verbose_name=_('Path Head'))
    path_tail = fields.CharField(
            max_length=63,
            verbose_name=_('Path Tail'))
    query_string = fields.CharField(
            blank=True,
            max_length=255,
            verbose_name=_('Query String'))

    objects = CurrentSiteManager()

    class Meta:
        abstract = True
        ordering = ['path_head', 'path_tail', 'query_string']
        unique_together = [('site', 'path_head', 'path_tail', 'query_string')]
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __str__(self):
        return self.full_path

    @staticmethod
    def autocomplete_search_fields():
        return ('path_head__icontains',
                'path_tail__icontains',
                'query_string__icontains')

    def get_full_path(self):
        if self.query_string:
            return '{0}?{1}'.format(self.get_path(), self.query_string)
        else:
            return self.get_path()
    get_full_path.short_description = _('Full Path')

    def get_path(self):
        return '{0}{1}'.format(self.path_head, self.path_tail)
    get_path.short_description = _('Path')

    full_path = property(get_full_path)
    path = property(get_path)


class AbstractPageView(models.Model):

    visit = models.ForeignKey(
            'metrics.Visit',
            on_delete=models.CASCADE,
            related_name='page_views',
            verbose_name=_('Visit'))
    page = models.ForeignKey(
            'metrics.Page',
            on_delete=models.CASCADE,
            related_name='page_views',
            verbose_name=_('Page'))
    previous_page_id = fields.IntegerField(
            blank=True,
            null=True,
            verbose_name=_('Previous Page ID'))
    next_page_id = fields.IntegerField(
            blank=True,
            null=True,
            verbose_name=_('Next Page ID'))
    status_code = fields.SmallIntegerField(
            verbose_name=_('Status Code'))
    date = models.DateTimeField(
            verbose_name=_('Date'))
    load_time = fields.FloatField(
            verbose_name=_('Load Time'))

    class Meta:
        abstract = True
        ordering = ['-date']
        verbose_name = _('Page View')
        verbose_name_plural = _('Page Views')

    _next_page_cache = Undefined
    _previous_page_cache = Undefined

    def get_next_page(self):
        if self._next_page_cache is Undefined:
            if self.next_page_id is None:
                self._next_page_cache = None
            else:
                self._next_page_cache = Page.objects.get(pk=self.next_page_id)

        return self._next_page_cache
    get_next_page.short_description = _('Next Page')

    def get_previous_page(self):
        if self._previous_page_cache is Undefined:
            if self.previous_page_id is None:
                self._previous_page_cache = None
            else:
                self._previous_page_cache = Page.objects.get(pk=self.previous_page_id)

        return self._previous_page_cache
    get_previous_page.short_description = _('Previous Page')

    next_page = property(get_next_page)
    previous_page = property(get_previous_page)


@python_2_unicode_compatible
class AbstractReferrer(models.Model):

    domain = fields.CharField(
            unique=True,
            max_length=63,
            verbose_name=_('Domain'))

    class Meta:
        abstract = True
        ordering = ['domain']
        verbose_name = _('Referrer')
        verbose_name_plural = _('Referrers')

    def __str__(self):
        return self.domain

    @staticmethod
    def autocomplete_search_fields():
        return ('domain__icontains', )


@python_2_unicode_compatible
class AbstractReferrerPage(models.Model):

    referrer = models.ForeignKey(
            'metrics.Referrer',
            on_delete=models.CASCADE,
            related_name='pages',
            verbose_name=_('Referrer'))
    full_path = fields.CharField(
            max_length=255,
            verbose_name=_('Path'))

    class Meta:
        abstract = True
        ordering = ['full_path']
        unique_together = [('referrer', 'full_path')]
        verbose_name = _('Referrer page')
        verbose_name_plural = _('Referrer pages')

    def __str__(self):
        return self.full_path

    @staticmethod
    def autocomplete_search_fields():
        return ('path__icontains', )


@python_2_unicode_compatible
class AbstractVisit(models.Model):

    site = models.ForeignKey(
            'sites.Site',
            on_delete=models.CASCADE,
            related_name='visits',
            verbose_name=_('Site'))
    visitor = models.ForeignKey(
            'metrics.Visitor',
            on_delete=models.CASCADE,
            related_name='visits',
            verbose_name=_('Visitor'))
    country = CountryField(
            null=True,
            related_name='visits')
    language = LanguageField(
            null=True,
            related_name='visits')
    region = RegionField(
            null=True,
            related_name='visits')
    browser = models.ForeignKey(
            'metrics.Browser',
            null=True,
            on_delete=models.CASCADE,
            related_name='visits',
            verbose_name=_('Browser'))
    engine = models.ForeignKey(
            'metrics.Engine',
            null=True,
            on_delete=models.CASCADE,
            related_name='visits',
            verbose_name=_('Engine'))
    platform = models.ForeignKey(
            'metrics.Platform',
            null=True,
            on_delete=models.CASCADE,
            related_name='visits',
            verbose_name=_('Platform'))
    referrer = models.ForeignKey(
            'metrics.Referrer',
            null=True,
            on_delete=models.CASCADE,
            related_name='visits',
            verbose_name=_('Referrer'))
    referrer_page = models.ForeignKey(
            'metrics.ReferrerPage',
            null=True,
            on_delete=models.CASCADE,
            related_name='visits',
            verbose_name=_('Referrer Page'))
    page_count = fields.SmallIntegerField(
            verbose_name=_('Page Views'))
    start_date = models.DateTimeField(
            db_index=True,
            verbose_name=_('Start Date'))
    end_date = models.DateTimeField(
            db_index=True,
            verbose_name=_('End Date'))
    user_agent = fields.CharField(
            max_length=255,
            verbose_name=_('User-Agent'))

    pages = models.ManyToManyField(
            'metrics.Page',
            blank=True,
            through='metrics.PageView',
            related_name='visits',
            verbose_name=_('Page Views'))

    objects = CurrentSiteManager()

    class Meta:
        abstract = True
        ordering = ['-start_date']
        verbose_name = _('Visit')
        verbose_name_plural = _('Visits')

    def __str__(self):
        args = (
            self.visitor,
            date_format(self.start_date, 'SHORT_DATE_FORMAT'),
        )
        return '{0} ({1})'.format(*args)

    def rebound(self):
        return (self.view_count == 1)
    rebound.boolean = True
    rebound.short_description = _('Rebound?')


@python_2_unicode_compatible
class AbstractVisitor(models.Model):

    site = models.ForeignKey(
            'sites.Site',
            on_delete=models.CASCADE,
            related_name='visitors',
            verbose_name=_('Site'))
    is_authenticated = fields.BooleanField(
            verbose_name=_('Is Authenticated?'))
    key = fields.CharField(
            max_length=32,
            db_index=True,
            verbose_name=_('Visitor Key'))

    objects = CurrentSiteManager()

    class Meta:
        abstract = True
        ordering = ['-id']
        verbose_name = _('Visitor')
        verbose_name_plural = _('Visitors')

    def __str__(self):
        return self.key

