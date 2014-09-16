# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime
from decimal import Decimal

from django import test
from django.utils import timezone
from django.utils import translation

from yepes.apps.registry import registry
from yepes.model_mixins import Displayable
from yepes.model_mixins.multilingual import TranslationDoesNotExist
from yepes.tests.model_mixins.models import (
    Article,
    Book,
    BookTranslation,
    Category,
    Image,
    Language,
    Product,
    ProductVariant,
)


class LoggedTest(test.TestCase):

    def test_timestamps(self):
        article = Article(title='Django for Dummies')
        self.assertIsNone(article.creation_date)
        self.assertIsNone(article.last_modified)

        article.save()
        self.assertIsNotNone(article.creation_date)
        self.assertIsNotNone(article.last_modified)

        creation_date = article.creation_date
        last_modified = article.last_modified
        article.save()
        self.assertEqual(
            article.creation_date,
            creation_date,
        )
        self.assertNotEqual(
            article.last_modified,
            last_modified,
        )

        last_modified = article.last_modified
        article.save(update_fields=['title'])
        self.assertNotEqual(
            article.last_modified,
            last_modified,
        )


class MetaDataTest(test.TestCase):

    def test_instance_methods(self):
        article = Article()
        article.title = 'Two Scoops of Django'
        article.content = (
            'This book is chock-full of material that will help you with'
            ' your Django projects.\n'
            'We’ll introduce you to various tips, tricks, patterns, code'
            ' snippets, and techniques that we’ve picked up over the years.'
            ' This book is a significant revision of the previous edition.'
        )
        self.assertEqual(
            article.get_meta_title(),
            'Two Scoops of Django',
        )
        self.assertEqual(
            article.get_meta_title(max_length=10, end_text='......'),
            'Two Scoops......',
        )
        self.assertEqual(
            article.get_meta_description(),
            'This book is chock-full of material that will help you with'
            ' your Django projects.'
            ' We’ll introduce you to various tips, tricks, patterns, code'
            ' snippets, and techniques that we’ve picked up...',
        )
        self.assertEqual(
            article.get_meta_description(max_words=5, end_text='......'),
            'This book is chock-full of......',
        )
        registry['core:STOP_WORDS'] = (
            'i', 'you', 'he', 'she', 'we', 'they',
            'my', 'your', 'his', 'her', 'our', 'their',
            'of',
            'the',
            'this', 'that',
            'and', 'or', 'xor',
            'is', 'are',
            'have', 'has', 'had',
        )
        self.assertEqual(
            article.get_meta_keywords(),
            'django, scoops, two, code,'
            ' help, picked, we\u2019ve,'
            ' chock, snippets, techniques',
        )
        self.assertEqual(
            article.get_meta_keywords(max_words=3),
            'django, scoops, two',
        )


class MultilingualTest(test.TestCase):

    def setUp(self):
        self.lang_en = Language.objects.create(
            tag='en',
            name='English',
        )
        self.lang_pl = Language.objects.create(
            tag='pl',
            name='Polish',
        )
        self.book = Book.objects.create(
            isbn=1234567890,
        )
        self.book_en = BookTranslation.objects.create(
            language=self.lang_en,
            title='Django for Dummies',
            description='Django described in simple words.',
            model=self.book,
        )
        self.book_pl = BookTranslation.objects.create(
            language=self.lang_pl,
            title='Django dla Idiotow',
            description='Django opisane w prostych slowach.',
            model=self.book,
        )

    def test_translated_attributes(self):
        # Translated attributes are returned in the active language.
        translation.activate('en')
        self.assertEqual(translation.get_language(), 'en')
        self.assertEqual(
            self.book.title,
            'Django for Dummies',
        )
        translation.activate('pl')
        self.assertEqual(translation.get_language(), 'pl')
        self.assertEqual(
            self.book.title,
            'Django dla Idiotow',
        )
        # If no translation is found, None is returned.
        translation.activate('fr')
        self.assertEqual(translation.get_language(), 'fr')
        self.assertIsNone(self.book.description)

        # Unless you deactivate MULTILINGUAL_FAIL_SILENTLY.
        # In this case, an exception is raised.
        with self.settings(MULTILINGUAL_FAIL_SILENTLY=False):
            translation.activate('de')
            self.assertEqual(translation.get_language(), 'de')
            with self.assertRaises(TranslationDoesNotExist):
                self.book.description

        # Or if you activate MULTILINGUAL_FALL_BACK_TO_DEFAULT.
        # In this case, the default translation is returned.
        with self.settings(MULTILINGUAL_FALL_BACK_TO_DEFAULT=True):
            translation.activate('it')
            self.assertEqual(translation.get_language(), 'it')
            self.assertEqual(
                self.book.description,
                'Django described in simple words.',
            )
        # Default translation can be changed from english
        # to any other by using MULTILINGUAL_DEFAULT.
        with self.settings(MULTILINGUAL_FALL_BACK_TO_DEFAULT=True,
                           MULTILINGUAL_DEFAULT='pl'):
            translation.activate('ar')
            self.assertEqual(translation.get_language(), 'ar')
            self.assertEqual(
                self.book.description,
                'Django opisane w prostych slowach.',
            )
        # If either the default translation can be found,
        # None is returned.
        with self.settings(MULTILINGUAL_FALL_BACK_TO_DEFAULT=True,
                           MULTILINGUAL_DEFAULT='zh'):
            translation.activate('zh')
            self.assertEqual(translation.get_language(), 'zh')
            self.assertIsNone(self.book.description)

        # Regardless the active translation, you can access
        # all translations.
        self.assertEqual(
            self.book.title_en,
            'Django for Dummies',
        )
        self.assertEqual(
            self.book.description_pl,
            'Django opisane w prostych slowach.',
        )
        translation.activate('en')   # Do not forget.


class NestableTest(test.TestCase):

    def setUp(self):
        self.books = Category.objects.create(
            name='Books',
        )
        self.classics = Category.objects.create(
            name='Classics',
            parent=self.books,
        )
        self.african = Category.objects.create(
            name='African',
            parent=self.classics,
        )
        self.european = Category.objects.create(
            name='European',
            parent=self.classics,
        )
        self.american = Category.objects.create(
            name='American',
            parent=self.classics,
        )
        self.asian = Category.objects.create(
            name='Asian',
            parent=self.classics,
        )
        self.australian = Category.objects.create(
            name='Australian & Oceanian',
            parent=self.classics,
        )

    def test_instance_methods(self):
        # ANCESTORS
        self.assertEqual(
            list(self.books.get_ancestors()),
            [],
        )
        self.assertEqual(
            list(self.classics.get_ancestors()),
            [self.books],
        )
        self.assertEqual(
            list(self.european.get_ancestors()),
            [self.books, self.classics],
        )
        self.assertEqual(
            list(self.european.get_ancestors(ascending=True, include_self=True)),
            [self.european, self.classics, self.books],
        )
        # CHILDREN
        self.assertEqual(
            list(self.books.get_children()),
            [self.classics],
        )
        self.assertEqual(
            list(self.classics.get_children()),
            [self.african, self.american, self.asian, self.australian, self.european],
        )
        self.assertEqual(
            list(self.european.get_children()),
            [],
        )
        # DESCENDANTS
        self.assertEqual(
            list(self.books.get_descendants()),
            [self.classics, self.african, self.american, self.asian, self.australian, self.european],
        )
        self.assertEqual(
            list(self.classics.get_descendants()),
            [self.african, self.american, self.asian, self.australian, self.european],
        )
        self.assertEqual(
            list(self.european.get_descendants()),
            [],
        )
        self.assertEqual(
            list(self.books.get_descendants(include_self=True)),
            [self.books, self.classics, self.african, self.american, self.asian, self.australian, self.european],
        )
        # LEVEL
        self.assertEqual(
            list(self.books.get_level()),
            [self.books],
        )
        self.assertEqual(
            list(self.classics.get_level()),
            [self.classics],
        )
        self.assertEqual(
            list(self.european.get_level()),
            [self.african, self.american, self.asian, self.australian, self.european],
        )
        # LEVEL NUMBER
        self.assertEqual(
            self.books.get_level_number(),
            0,
        )
        self.assertEqual(
            self.classics.get_level_number(),
            1,
        )
        self.assertEqual(
            self.european.get_level_number(),
            2,
        )
        # PARENT
        self.assertEqual(
            self.books.get_parent(),
            None,
        )
        self.assertEqual(
            self.classics.get_parent(),
            self.books,
        )
        self.assertEqual(
            self.european.get_parent(),
            self.classics,
        )
        # ROOT
        self.assertEqual(
            self.books.get_root(),
            self.books,
        )
        self.assertEqual(
            self.classics.get_root(),
            self.books,
        )
        self.assertEqual(
            self.european.get_root(),
            self.books,
        )
        # SIBLINGS
        self.assertEqual(
            list(self.books.get_siblings()),
            [],
        )
        self.assertEqual(
            list(self.classics.get_siblings()),
            [],
        )
        self.assertEqual(
            list(self.european.get_siblings()),
            [self.african, self.american, self.asian, self.australian],
        )
        self.assertEqual(
            list(self.european.get_siblings(include_self=True)),
            [self.african, self.american, self.asian, self.australian, self.european],
        )


class OrderableTest(test.TestCase):

    def test_model_options(self):
        self.assertIsNone(Language._meta.filter_field)
        self.assertTrue(Language._meta.get_field('index').db_index)
        self.assertEqual(
            Language._meta.index_together,
            []
        )
        self.assertEqual(Image._meta.filter_field, 'article')
        self.assertFalse(Image._meta.get_field('index').db_index)
        self.assertEqual(
            Image._meta.index_together,
            [('article', 'index')]
        )

    def test_simple_ordering(self):
        lang_en = Language.objects.create(
            tag='en',
            name='English',
        )
        lang_pl = Language.objects.create(
            tag='pl',
            name='Polish',
        )
        lang_fr = Language.objects.create(
            tag='fr',
            name='French',
        )
        lang_de = Language.objects.create(
            tag='de',
            name='German',
        )
        self.assertEqual(lang_en.index, 0)
        self.assertEqual(lang_pl.index, 1)
        self.assertEqual(lang_fr.index, 2)
        self.assertEqual(lang_de.index, 3)
        self.assertEqual(
            list(Language.objects.all()),
            [lang_en, lang_pl, lang_fr, lang_de],
        )
        self.assertEqual(
            lang_pl.get_next_in_order(),
            lang_fr,
        )
        self.assertEqual(
            lang_pl.get_previous_in_order(),
            lang_en,
        )
        self.assertIsNone(lang_de.get_next_in_order())
        self.assertIsNone(lang_en.get_previous_in_order())

        lang_pl.delete()
        lang_en = Language.objects.get(tag='en')
        lang_fr = Language.objects.get(tag='fr')
        lang_de = Language.objects.get(tag='de')
        self.assertEqual(lang_en.index, 0)
        self.assertEqual(lang_fr.index, 1)
        self.assertEqual(lang_de.index, 2)
        self.assertEqual(
            list(Language.objects.all()),
            [lang_en, lang_fr, lang_de],
        )
        self.assertEqual(
            lang_fr.get_next_in_order(),
            lang_de,
        )
        self.assertEqual(
            lang_fr.get_previous_in_order(),
            lang_en,
        )
        self.assertIsNone(lang_de.get_next_in_order())
        self.assertIsNone(lang_en.get_previous_in_order())

    def test_order_with_respect_to(self):
        article_1 = Article.objects.create(
            title='Django for Dummies',
        )
        article_2 = Article.objects.create(
            title='Two Scoops of Django',
        )
        image_1 = article_1.images.create()
        image_2 = article_1.images.create()
        image_3 = article_1.images.create()
        image_4 = article_2.images.create()
        image_5 = article_2.images.create()
        image_6 = article_2.images.create()

        self.assertEqual(image_1.article_id, article_1.pk)
        self.assertEqual(image_1.index, 0)
        self.assertEqual(image_2.article_id, article_1.pk)
        self.assertEqual(image_2.index, 1)
        self.assertEqual(image_3.article_id, article_1.pk)
        self.assertEqual(image_3.index, 2)
        self.assertEqual(image_4.article_id, article_2.pk)
        self.assertEqual(image_4.index, 0)
        self.assertEqual(image_5.article_id, article_2.pk)
        self.assertEqual(image_5.index, 1)
        self.assertEqual(image_6.article_id, article_2.pk)
        self.assertEqual(image_6.index, 2)
        self.assertEqual(
            list(article_1.images.all()),
            [image_1, image_2, image_3],
        )
        self.assertEqual(
            list(article_2.images.all()),
            [image_4, image_5, image_6],
        )
        self.assertEqual(
            list(Article.objects.all()),
            [article_1, article_2],
        )
        self.assertEqual(
            list(Image.objects.all()),
            [image_1, image_2, image_3, image_4, image_5, image_6],
        )
        self.assertEqual(
            image_2.get_next_in_order(),
            image_3,
        )
        self.assertEqual(
            image_2.get_previous_in_order(),
            image_1,
        )
        self.assertIsNone(image_3.get_next_in_order())
        self.assertIsNone(image_1.get_previous_in_order())

        image_2.delete()
        image_1 = Image.objects.get(pk=1)
        image_3 = Image.objects.get(pk=3)
        image_4 = Image.objects.get(pk=4)
        image_5 = Image.objects.get(pk=5)
        image_6 = Image.objects.get(pk=6)
        self.assertEqual(image_1.article_id, article_1.pk)
        self.assertEqual(image_1.index, 0)
        self.assertEqual(image_3.article_id, article_1.pk)
        self.assertEqual(image_3.index, 1)
        self.assertEqual(image_4.article_id, article_2.pk)
        self.assertEqual(image_4.index, 0)
        self.assertEqual(image_5.article_id, article_2.pk)
        self.assertEqual(image_5.index, 1)
        self.assertEqual(image_6.article_id, article_2.pk)
        self.assertEqual(image_6.index, 2)
        self.assertEqual(
            list(article_1.images.all()),
            [image_1, image_3],
        )
        self.assertEqual(
            list(article_2.images.all()),
            [image_4, image_5, image_6],
        )
        self.assertEqual(
            list(Article.objects.all()),
            [article_1, article_2],
        )
        self.assertEqual(
            list(Image.objects.all()),
            [image_1, image_3, image_4, image_5, image_6],
        )
        self.assertEqual(
            image_1.get_next_in_order(),
            image_3,
        )
        self.assertEqual(
            image_3.get_previous_in_order(),
            image_1,
        )
        self.assertIsNone(image_3.get_next_in_order())
        self.assertIsNone(image_1.get_previous_in_order())


class PublishableTest(test.TestCase):

    def setUp(self):
        self.article_1 = Article.objects.create(
            title='Django for Dummies',
            publish_status=Article.PUBLISHED,
            publish_from=None,
            publish_to=None,
        )
        self.article_2 = Article.objects.create(
            title='Two Scoops of Django',
            publish_status=Article.DRAFT,
            publish_from=None,
            publish_to=None,
        )
        self.article_3 = Article.objects.create(
            title='The Django Book',
            publish_status=Article.HIDDEN,
            publish_from=None,
            publish_to=None,
        )
        self.article_4 = Article.objects.create(
            title='The Definitive Guide to Django',
            publish_status=Article.PUBLISHED,
            publish_from=datetime(2000, 1, 1, tzinfo=timezone.utc),
            publish_to=datetime(2004, 12, 31, tzinfo=timezone.utc),
        )

    def test_instance_methods(self):
        self.assertTrue(self.article_1.is_published())
        self.assertFalse(self.article_1.is_draft())
        self.assertFalse(self.article_1.is_hidden())

        self.assertFalse(self.article_2.is_published())
        self.assertTrue(self.article_2.is_draft())
        self.assertFalse(self.article_2.is_hidden())

        self.assertFalse(self.article_3.is_published())
        self.assertFalse(self.article_3.is_draft())
        self.assertTrue(self.article_3.is_hidden())

        self.assertFalse(self.article_4.is_published())
        self.assertFalse(self.article_4.is_draft())
        self.assertFalse(self.article_4.is_hidden())

        timestamp = datetime(1999, 12, 31, tzinfo=timezone.utc)
        self.assertFalse(self.article_4.is_published(date=timestamp))

        timestamp = datetime(2005, 1, 1, tzinfo=timezone.utc)
        self.assertFalse(self.article_4.is_published(date=timestamp))

        timestamp = datetime(2002, 6, 15, tzinfo=timezone.utc)
        self.assertTrue(self.article_4.is_published(date=timestamp))

    def test_manager_methods(self):
        self.assertEqual(
            list(Article.objects.published()),
            [self.article_1]
        )
        self.assertEqual(
            list(Article.objects.unpublished()),
            [self.article_4]
        )
        timestamp = datetime(2002, 6, 15, tzinfo=timezone.utc)
        self.assertEqual(
            list(Article.objects.published(date=timestamp)),
            [self.article_1, self.article_4]
        )
        self.assertEqual(
            list(Article.objects.unpublished(date=timestamp)),
            []
        )


class SearchableTest(test.TestCase):

    def setUp(self):
        self.article_1 = Article.objects.create(
            title='Two Scoops of Django',
            content=(
                'This book is chock-full of material that will help you with'
                ' your Django projects.\n'
                'We’ll introduce you to various tips, tricks, patterns, code'
                ' snippets, and techniques that we’ve picked up over the years.'
                ' This book is a significant revision of the previous edition.'
            ),
        )
        self.article_2 = Article.objects.create(
            title='The Django Book',
            content=(
                'You’re reading _The Django Book_, first published in December'
                ' 2007 (and updated in 2009) by Apress as _The Definitive Guide'
                ' to Django: Web Development Done Right_.\n\n'
                'We’ve released this book freely for a couple of reasons.'
                ' First, we love Django and we want it to be as accessible as'
                ' possible. Many programmers learn their craft from'
                ' well-written technical material, so we set out to create a'
                ' top-notch guide and reference to Django.'
                'Second, it turns out that writing books about technology is'
                ' fundamentally difficult: your words are often outdated before'
                ' the book even reaches the printer. On the web, however,'
                ' “the ink is never dry” — we can (and will!) keep the book'
                ' updated.'
            ),
        )
        self.article_3 = Article.objects.create(
            title='The Definitive Guide to Django',
            content=(
                'Django, the Python–based equivalent to the Ruby on Rails web'
                ' development framework, is hottest topics in web development.'
                ' In _The Definitive Guide to Django: Web Development Done'
                ' Right_, **Adrian Holovaty**, one of Django’s creators, and'
                ' Django lead developer **Jacob Kaplan–Moss** show you how'
                ' they use this framework to create award–winning web sites.'
            ),
        )
        self.product_1 = Product.objects.create(
            name='Two Scoops of Django',
            description=(
                'This book is chock-full of material that will help you with'
                ' your Django projects.\n'
                'We’ll introduce you to various tips, tricks, patterns, code'
                ' snippets, and techniques that we’ve picked up over the years.'
                ' This book is a significant revision of the previous edition.'
            ),
        )
        self.variant_1 = self.product_1.variants.create(
            sku='TSOD-DJANGO-16',
            name='Two Scoops of Django: Best Practices for Django 1.6',
        )
        self.variant_2 = self.product_1.variants.create(
            sku='TSOD-DJANGO-15',
            name='Two Scoops of Django: Best Practices for Django 1.5',
        )
        self.product_2 = Product.objects.create(
            name='The Django Book',
            description=(
                'You’re reading _The Django Book_, first published in December'
                ' 2007 (and updated in 2009) by Apress as _The Definitive Guide'
                ' to Django: Web Development Done Right_.\n\n'
                'We’ve released this book freely for a couple of reasons.'
                ' First, we love Django and we want it to be as accessible as'
                ' possible. Many programmers learn their craft from'
                ' well-written technical material, so we set out to create a'
                ' top-notch guide and reference to Django.'
                'Second, it turns out that writing books about technology is'
                ' fundamentally difficult: your words are often outdated before'
                ' the book even reaches the printer. On the web, however,'
                ' “the ink is never dry” — we can (and will!) keep the book'
                ' updated.'
            ),
        )
        self.variant_3 = self.product_2.variants.create(
            sku='TDB',
            name='The Django Book',
        )
        self.product_3 = Product.objects.create(
            name='The Definitive Guide to Django',
            description=(
                'Django, the Python–based equivalent to the Ruby on Rails web'
                ' development framework, is hottest topics in web development.'
                ' In _The Definitive Guide to Django: Web Development Done'
                ' Right_, **Adrian Holovaty**, one of Django’s creators, and'
                ' Django lead developer **Jacob Kaplan–Moss** show you how'
                ' they use this framework to create award–winning web sites.'
            ),
        )
        self.variant_4 = self.product_3.variants.create(
            sku='TDGTD',
            name='The Definitive Guide to Django',
        )

    def test_manager_methods(self):
        manager = Displayable.objects
        self.assertEqual(len(manager.search('guide')), 4)
        self.assertEqual(len(manager.search('technical material')), 4)
        self.assertEqual(len(manager.search('+technical material')), 2)
        self.assertEqual(len(manager.search('-technical material')), 2)
        self.assertEqual(len(manager.search('"technical material"')), 2)
        self.assertEqual(
            manager.search('guide'),
            [self.article_3, self.product_3, self.article_2, self.product_2],
        )
        self.assertEqual(
            manager.search('technical material'),
            [self.article_2, self.product_2, self.article_1, self.product_1],
        )
        self.assertEqual(
            manager.search('+technical material'),
            [self.article_2, self.product_2],
        )
        self.assertEqual(
            manager.search('-technical material'),
            [self.article_1, self.product_1],
        )
        self.assertEqual(
            manager.search('"technical material"'),
            [self.article_2, self.product_2],
        )
        self.assertEqual(
            manager.search('+"Django" -"development framework"'),
            [self.product_1, self.article_2, self.product_2, self.article_1],
        )
        self.assertEqual(
            manager.search('"+Django" "-development framework"'),
            [self.product_1, self.article_2, self.product_2, self.article_1],
        )

    def test_queryset_methods(self):
        qs = Article.objects.get_queryset()
        self.assertEqual(len(qs.search('guide')), 2)
        self.assertEqual(len(qs.search('technical material')), 2)
        self.assertEqual(len(qs.search('+technical material')), 1)
        self.assertEqual(len(qs.search('-technical material')), 1)
        self.assertEqual(len(qs.search('"technical material"')), 1)
        self.assertEqual(
            list(qs.search('guide')),
            [self.article_3, self.article_2],
        )
        self.assertEqual(
            list(qs.search('technical material')),
            [self.article_2, self.article_1],
        )
        self.assertEqual(
            list(qs.search('+technical material')),
            [self.article_2],
        )
        self.assertEqual(
            list(qs.search('-technical material')),
            [self.article_1],
        )
        self.assertEqual(
            list(qs.search('"technical material"')),
            [self.article_2],
        )
        self.assertEqual(
            list(qs.search('+"Django" -"development framework"')),
            [self.article_2, self.article_1],
        )
        self.assertEqual(
            list(qs.search('"+Django" "-development framework"')),
            [self.article_2, self.article_1],
        )

    def test_search_across_related_fields(self):
        self.assertEqual(
            Product.objects.search('TDGTD'),
            [self.product_3],
        )
        self.assertEqual(
            Product.objects.search('Django -TDGTD'),
            [self.product_1, self.product_2],
        )
        self.assertEqual(
            Product.objects.search('DJANGO'),
            [self.product_1, self.product_2, self.product_3],
        )


class SluggedTest(test.TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name='Educational Toys',
        )

    def test_instance_methods(self):
        self.assertEqual(
            self.category.natural_key(),
            ('educational-toys', ),
        )
        self.assertEqual(
            self.category.get_absolute_url(),
            '/categories/educational-toys.html',
        )
        self.assertEqual(
            self.category.get_full_url(),
            'http://example.com/categories/educational-toys.html',
        )
        self.assertEqual(
            self.category.get_link(),
            '<a href="/categories/educational-toys.html">Educational Toys</a>',
        )
        self.assertEqual(
            self.category.onsite_link(),
            '<a href="http://example.com/categories/educational-toys.html">View on site</a>',
        )

