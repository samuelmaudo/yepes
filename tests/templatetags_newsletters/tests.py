# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.test import SimpleTestCase
from django.template import Context, Template

from yepes.templatetags.newsletters import (
    ImageUrlTag,
    LinkUrlTag,
    MessageUrlTag,
    PrerenderedImageTag,
    PrerenderedLinkTag,
    ProfileUrlTag,
    ResubscriptionUrlTag,
    SubscriptionUrlTag,
    UnsubscriptionUrlTag,
)
from yepes.test_mixins import TemplateTagsMixin


class NewsletterTagsTest(TemplateTagsMixin, SimpleTestCase):

    required_libraries = ['newsletters']

    def test_image_url_syntax(self):
        self.checkSyntax(
            ImageUrlTag,
            '{% image_url name %}',
        )

    def test_link_url_syntax(self):
        self.checkSyntax(
            LinkUrlTag,
            '{% link_url url %}',
        )

    def test_message_url_syntax(self):
        self.checkSyntax(
            MessageUrlTag,
            '{% message_url %}',
        )

    def test_prerendered_image_syntax(self):
        self.checkSyntax(
            PrerenderedImageTag,
            '{% prerendered_image guid %}',
        )

    def test_prerendered_link_syntax(self):
        self.checkSyntax(
            PrerenderedLinkTag,
            '{% prerendered_link guid %}',
        )

    def test_profile_url_syntax(self):
        self.checkSyntax(
            ProfileUrlTag,
            '{% profile_url %}',
        )

    def test_resubscription_url_syntax(self):
        self.checkSyntax(
            ResubscriptionUrlTag,
            '{% resubscription_url %}',
        )

    def test_subscription_url_syntax(self):
        self.checkSyntax(
            SubscriptionUrlTag,
            '{% subscription_url %}',
        )

    def test_unsubscription_url_syntax(self):
        self.checkSyntax(
            UnsubscriptionUrlTag,
            '{% unsubscription_url %}',
        )

