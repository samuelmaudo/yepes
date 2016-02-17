# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import F, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import six
from django.utils.encoding import force_text
from django.utils.itercompat import is_iterable
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import (
    RedirectView,
    TemplateView,
    View,
)

from aggregate_if import Count

from yepes.contrib.newsletters.utils import prerender, render
from yepes.loading import get_class, get_model
from yepes.utils.views import decorate_view
from yepes.views import FormView, UpdateView

Click = get_model('newsletters', 'Click')
Delivery = get_model('newsletters', 'Delivery')
Message = get_model('newsletters', 'Message')
Open = get_model('newsletters', 'Open')
OpenManager = Open._default_manager
Subscriber = get_model('newsletters', 'Subscriber')
SubscriberManager = Subscriber._default_manager
Subscription = get_model('newsletters', 'Subscription')

ProfileForm = get_class('newsletters.forms', 'ProfileForm')
DispatchForm = get_class('newsletters.forms', 'DispatchForm')
SubscriptionForm = get_class('newsletters.forms', 'SubscriptionForm')
UnsubscriptionForm = get_class('newsletters.forms', 'UnsubscriptionForm')
UnsubscriptionReasonForm = get_class('newsletters.forms', 'UnsubscriptionReasonForm')

ImageMixin = get_class('newsletters.view_mixins', 'ImageMixin')
LinkMixin = get_class('newsletters.view_mixins', 'LinkMixin')
MessageMixin = get_class('newsletters.view_mixins', 'MessageMixin')
NewsletterMixin = get_class('newsletters.view_mixins', 'NewsletterMixin')
SubscriberMixin = get_class('newsletters.view_mixins', 'SubscriberMixin')


class DispatchView(UpdateView):

    context_object_name = 'original'
    delivery_model = Delivery
    form_class = DispatchForm
    model = Message
    subscriber_model = Subscriber
    subtitle = _('When and to whom do you want to send it?')
    title = _('Send Message')

    def form_valid(self, form):
        form_data = form.cleaned_data
        delivery_manager = self.delivery_model._default_manager
        subscriber_manager = self.subscriber_model._default_manager

        previous_deliveries = delivery_manager.get_queryset(
        ).filter(message=self.object
        ).values_list('subscriber_id')

        subscribers = subscriber_manager.get_queryset(
        ).filter(~Q(pk__in=previous_deliveries)
        ).enabled()

        if form_data.get('score_filter'):
            subscribers = subscribers.filter(**{
                'score__{0}'.format(form_data['score_filter']):
                form_data['score_filter_value'],
            })

        if form_data.get('bounce_filter'):
            subscribers = subscribers.annotate(bounce_count=Count(
                'deliveries',
                Q(deliveries__is_bounced=True)),
            ).filter(**{
                'bounce_count__{0}'.format(form_data['bounce_filter']):
                form_data['bounce_filter_value'],
            })

        if form_data.get('click_filter'):
            subscribers = subscribers.annotate(click_count=Count(
                'deliveries',
                Q(deliveries__is_clicked=True)),
            ).filter(**{
                'click_count__{0}'.format(form_data['click_filter']):
                form_data['click_filter_value'],
            })

        if form_data.get('open_filter'):
            subscribers = subscribers.annotate(open_count=Count(
                'deliveries',
                Q(deliveries__is_opened=True)),
            ).filter(**{
                'open_count__{0}'.format(form_data['open_filter']):
                form_data['open_filter_value'],
            })

        if form_data.get('tags_filter') == 'eq':
            subscribers = subscribers.filter(
                tags=form_data['tags_filter_value'],
            )
        elif form_data.get('tags_filter') == 'ne':
            subscribers = subscribers.filter(
                ~Q(tags=form_data['tags_filter_value']),
            )

        subscribers = subscribers.values_list(
            'pk',
            'email_domain_id',
        ).order_by('?')

        deliveries = []
        for subscriber_id, domain_id in subscribers:
            delivery = self.delivery_model()
            delivery.message = self.object
            delivery.newsletter_id = self.object.newsletter_id
            delivery.subscriber_id = subscriber_id
            delivery.domain_id = domain_id
            delivery.date = form_data['date']
            deliveries.append(delivery)

        delivery_manager.bulk_create(deliveries)

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        model = self.get_model()
        context = {
            'app_label': model._meta.app_label,
            'opts': model._meta,
            'subtitle': self.subtitle,
            'title': self.title,
        }
        context.update(kwargs)
        return super(DispatchView, self).get_context_data(**context)

    def get_form_kwargs(self):
        kwargs = {'initial': self.get_initial()}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_success_url(self):
        return reverse('admin:newsletters_message_change',
                       args=(self.object.pk, ))

    def get_template_names(self):
        names = []
        if isinstance(self.template_name, six.string_types):
            names.append(self.template_name)
        elif is_iterable(self.template_name):
            names.extend(self.template_name)

        model = self.get_model()
        info = (model._meta.app_label, model._meta.model_name)
        names.insert(-1, 'admin/{0}/{1}/dispatch.html'.format(*info))
        return names

    def log_dispatch(self, request, object):
        LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(object).pk,
                object_id=object.pk,
                object_repr=force_text(object),
                action_flag=CHANGE)


class ImageView(SubscriberMixin, MessageMixin, ImageMixin, View):

    require_image = True

    def get(self, request, *args, **kwargs):
        image = self.get_image()
        message = self.get_message()
        subscriber = self.get_subscriber()

        if message is not None and subscriber is not None:
            open = Open()
            open.message = message
            open.subscriber = subscriber
            # Unlike clicks, openings only should be registered the first time.
            if not OpenManager.filter(
                    message=message,
                    subscriber=subscriber).exists():
                # This involves more code than just call ``get_or_create()``
                # but is more efficient because ``get_or_create()`` tries to
                # retrieve the entire record.
                open.save()

        image_data = image.image.read()
        if image_data.startswith(b'\xff\xd8'):
            image_type = 'image/jpeg'
        elif image_data.startswith(b'\x89PNG\r\n\x1a\n'):
            image_type = 'image/png'
        elif image_data.startswith(b'GIF8'):
            image_type = 'image/gif'
        elif image_data.startswith(b'WEBP', 8):
            image_type = 'image/webp'

        response = HttpResponse(image_data, content_type=image_type)
        response['Content-Length'] = len(image_data)
        return response


class LinkView(SubscriberMixin, MessageMixin, LinkMixin, RedirectView):

    permanent = False
    require_link = True

    def get_redirect_url(self, *args, **kwargs):
        link = self.get_link()
        message = self.get_message()
        subscriber = self.get_subscriber()

        if message is not None and subscriber is not None:
            click = Click()
            click.link = link
            click.message = message
            click.subscriber = subscriber
            click.save()

        return link.url


class MessageView(SubscriberMixin, MessageMixin, View):

    require_message = True

    def get(self, request, *args, **kwargs):
        message = self.get_message()
        subscriber = self.get_subscriber()

        if subscriber is not None:
            # Subscribers cannot access this view
            # without opening the message.
            open = Open()
            open.message = message
            open.subscriber = subscriber
            if not OpenManager.filter(
                    message=message,
                    subscriber=subscriber).exists():
                open.save()

        html = self.get_prerendered_html(message)
        context = {
            'subscriber': subscriber,
            'newsletter': message.newsletter,
            'message': message,
        }
        return HttpResponse(render(html, context))

    def get_prerendered_html(self, message):
        key = 'yepes.newsletters.message.{0}'.format(message.guid)
        html = cache.get(key)
        if html is None or self.request.user.is_staff:

            context = {
                'subscriber': None, # Subscriber must not be specified here.
                'newsletter': message.newsletter,
                'message': message,
            }
            html = prerender(message.html, context)
            cache.set(key, html)

        return html


@decorate_view(
    csrf_protect,
    never_cache,
)
class ProfileView(SubscriberMixin, NewsletterMixin, MessageMixin, FormView):
    """
    Allows subscribers to change their preferences, including subscriptions.

    NOTE: Newsletter and message mixins are not strictly necessary for this
          view. However, they may be useful for render unsubscription links.

    """
    form_class = ProfileForm
    require_subscriber = True

    def get_initial(self):
        initial = super(ProfileView, self).get_initial()
        subscriber = self.get_subscriber()
        initial['email_address'] = subscriber.email_address
        initial['first_name'] = subscriber.first_name
        initial['last_name'] = subscriber.last_name
        return initial

    def get_success_url(self):
        return reverse('profile', kwargs={
            'subscriber_guid': self.get_subscriber().guid,
        })

    def get_template_names(self):
        names = []
        if isinstance(self.template_name, six.string_types):
            names.append(self.template_name)
        elif is_iterable(self.template_name):
            names.extend(self.template_name)

        args = (Subscription._meta.app_label, )
        names.insert(-1, '{0}/profile.html'.format(*args))
        return names

    def form_valid(self, form):
        subscriber = self.get_subscriber()
        subscriber.first_name = form.cleaned_data['first_name']
        subscriber.last_name = form.cleaned_data['last_name']
        subscriber.set_email(form.cleaned_data['email_address'])
        subscriber.save()
        return super(ProfileView, self).form_valid(form)


class ResubscriptionView(SubscriberMixin, NewsletterMixin, TemplateView):

    form_class = UnsubscriptionReasonForm
    require_newsletter = True
    require_subscriber = True

    def get(self, request, *args, **kwargs):
        subscriber = self.get_subscriber()
        subscriber.resubscribe_to(self.get_newsletter())
        return super(ResubscriptionView, self).get(request, *args, **kwargs)

    def get_template_names(self):
        names = []
        if isinstance(self.template_name, six.string_types):
            names.append(self.template_name)
        elif is_iterable(self.template_name):
            names.extend(self.template_name)

        args = (Subscription._meta.app_label, )
        names.extend([
            '{0}/resubscription.html'.format(*args),
        ])
        return names


@decorate_view(
    csrf_protect,
    never_cache,
)
class SubscriptionView(SubscriberMixin, NewsletterMixin, FormView):

    form_class = SubscriptionForm
    success_url = reverse_lazy('subscription')

    def form_valid(self, form):
        subscriber = self.get_subscriber(form)
        subscriber.subscribe_to(form.cleaned_data['newsletter'])
        return super(SubscriptionView, self).form_valid(form)

    def get_initial(self):
        initial = super(SubscriptionView, self).get_initial()
        if 'newsletter' not in initial:
            initial['newsletter'] = self.get_newsletter()
        if 'email_address' not in initial and self.get_subscriber():
            initial['email_address'] = self.get_subscriber().email_address
        return initial

    def get_subscriber(self, form=None):
        subscriber = super(SubscriptionView, self).get_subscriber()
        if subscriber is None and form is not None:

            address = form.cleaned_data['email_address']
            try:
                subscriber = SubscriberManager.get(email_address=address)
            except Subscriber.DoesNotExist:
                subscriber = Subscriber()
                subscriber.set_email(address)

            subscriber.first_name = form.cleaned_data['first_name']
            subscriber.last_name = form.cleaned_data['last_name']
            subscriber.save()

        return subscriber

    def get_template_names(self):
        names = []
        if isinstance(self.template_name, six.string_types):
            names.append(self.template_name)
        elif is_iterable(self.template_name):
            names.extend(self.template_name)

        args = (Subscription._meta.app_label, )
        names.insert(-1, '{0}/subscription.html'.format(*args))
        return names


@decorate_view(
    csrf_protect,
    never_cache,
)
class UnsubscriptionView(SubscriberMixin, NewsletterMixin, MessageMixin, FormView):

    form_class = UnsubscriptionForm

    def get(self, request, *args, **kwargs):
        newsletter = self.get_newsletter()
        subscriber = self.get_subscriber()
        if newsletter is not None and subscriber is not None:
            subscriber.unsubscribe_from(
                newsletter,
                last_message=self.get_message())
            return HttpResponseRedirect(self.get_success_url(subscriber, newsletter))
        else:
            return super(UnsubscriptionView, self).get(request, *args, **kwargs)

    def get_initial(self):
        initial = super(UnsubscriptionView, self).get_initial()
        if 'newsletter' not in initial:
            initial['newsletter'] = self.get_newsletter()
        if 'email_address' not in initial and self.get_subscriber():
            initial['email_address'] = self.get_subscriber().email_address
        return initial

    def get_success_url(self, subscriber, newsletter):
        if subscriber is None or newsletter is None:
            return reverse('unsubscription')
        else:
            return reverse('unsubscription_reason', kwargs={
                'subscriber_guid': subscriber.guid,
                'newsletter_guid': newsletter.guid,
            })

    def get_template_names(self):
        names = []
        if isinstance(self.template_name, six.string_types):
            names.append(self.template_name)
        elif is_iterable(self.template_name):
            names.extend(self.template_name)

        args = (Subscription._meta.app_label, )
        names.insert(-1, '{0}/unsubscription.html'.format(*args))
        return names

    def form_valid(self, form):
        newsletter = self.get_newsletter()
        if newsletter is None:
            newsletter = form.cleaned_data['newsletter']

        subscriber = self.get_subscriber()
        if subscriber is None:
            address = form.cleaned_data['email_address']
            try:
                subscriber = SubscriberManager.get(email_address=address)
            except Subscriber.DoesNotExist:
                pass

        if subscriber is not None:
            subscriber.unsubscribe_from(
                newsletter,
                last_message=self.get_message())

        return HttpResponseRedirect(self.get_success_url(subscriber, newsletter))


class UnsubscriptionReasonView(SubscriberMixin, NewsletterMixin, FormView):

    form_class = UnsubscriptionReasonForm
    require_newsletter = True
    require_subscriber = True
    success_url = reverse_lazy('unsubscription')

    def get_template_names(self):
        names = []
        if isinstance(self.template_name, six.string_types):
            names.append(self.template_name)
        elif is_iterable(self.template_name):
            names.extend(self.template_name)

        args = (Subscription._meta.app_label, )
        names.insert(-1, '{0}/unsubscription_reason.html'.format(*args))
        return names

    def get_unsubscription(self):
        qs = self.get_subscriber().unsubscriptions.all()
        qs = qs.filter(newsletter=self.get_newsletter())
        qs = qs.order_by('date')
        return qs.last()

    def form_valid(self, form):
        unsubscription = self.get_unsubscription()
        if unsubscription is not None:
            unsubscription.reason = form.cleaned_data['reason']
            unsubscription.save(update_fields=['reason'])
        return super(UnsubscriptionReasonView, self).form_valid(form)

