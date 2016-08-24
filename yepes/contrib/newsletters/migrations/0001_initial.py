# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import yepes.model_mixins.illustrated
import re
import django.db.models.deletion
import django.utils.timezone
import django.core.validators
import yepes.fields


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0001_initial'),
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meta_title', yepes.fields.CharField(help_text='Optional title to be used in the HTML title tag. If left blank, the main title field will be used.', max_length=127, verbose_name='Title', blank=True)),
                ('meta_description', yepes.fields.TextField(help_text='Optional description to be used in the description meta tag. If left blank, the content field will be used.', verbose_name='Description', blank=True)),
                ('meta_keywords', yepes.fields.CommaSeparatedField(separator=', ', blank=True, help_text='Optional keywords to be used in the keywords meta tag. If left blank, will be extracted from the description.', verbose_name='Keywords')),
                ('slug', yepes.fields.SlugField(help_text='URL friendly version of the main title. It is usually all lowercase and contains only letters, numbers and hyphens.', unique=True, verbose_name='Slug')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('index', yepes.fields.IntegerField(default=0, min_value=0, db_index=True, verbose_name='Index', blank=True)),
                ('guid', yepes.fields.GuidField(charset='0123456789abcdef', editable=False, max_length=7, unique=True, verbose_name='Global Unique Identifier')),
                ('name', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Name')),
                ('description', yepes.fields.RichTextField(verbose_name='Description', blank=True)),
                ('description_html', yepes.fields.TextField(verbose_name='Description', editable=False, db_column='description_html', blank=True)),
                ('is_published', yepes.fields.BooleanField(default=True, verbose_name='Is Published?')),
                ('sender_name', yepes.fields.CharField(max_length=127, verbose_name="Sender's Name")),
                ('sender_address', yepes.fields.CharField(max_length=127, verbose_name="Sender's Address")),
                ('reply_to_name', yepes.fields.CharField(max_length=127, verbose_name='Reply To Name', blank=True)),
                ('reply_to_address', yepes.fields.CharField(max_length=127, verbose_name='Reply To Address', blank=True)),
                ('return_path_name', yepes.fields.CharField(max_length=127, verbose_name='Return To Name', blank=True)),
                ('return_path_address', yepes.fields.CharField(max_length=127, verbose_name='Return To Address', blank=True)),
                ('connection', yepes.fields.CachedForeignKey(related_name='newsletters', verbose_name='E-mail Connection', to='emails.Connection')),
            ],
            options={
                'verbose_name': 'Newsletter',
                'verbose_name_plural': 'Newsletters',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meta_title', yepes.fields.CharField(help_text='Optional title to be used in the HTML title tag. If left blank, the main title field will be used.', max_length=127, verbose_name='Title', blank=True)),
                ('meta_description', yepes.fields.TextField(help_text='Optional description to be used in the description meta tag. If left blank, the content field will be used.', verbose_name='Description', blank=True)),
                ('meta_keywords', yepes.fields.CommaSeparatedField(separator=', ', blank=True, help_text='Optional keywords to be used in the keywords meta tag. If left blank, will be extracted from the description.', verbose_name='Keywords')),
                ('slug', yepes.fields.SlugField(help_text='URL friendly version of the main title. It is usually all lowercase and contains only letters, numbers and hyphens.', unique=True, verbose_name='Slug')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('newsletter', models.ForeignKey(related_name='messages', verbose_name='Newsletter', to='newsletters.Newsletter')),
                ('guid', yepes.fields.GuidField(charset='0123456789abcdef', editable=False, max_length=15, unique=True, verbose_name='Global Unique Identifier')),
                ('subject', yepes.fields.CharField(max_length=255, verbose_name='Subject')),
                ('html', yepes.fields.TextField(verbose_name='HTML Version')),
                ('text', yepes.fields.TextField(verbose_name='Plain Text Version', blank=True)),
                ('is_sent', yepes.fields.BooleanField(default=False, verbose_name='Is Sent?', editable=False)),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
        ),
        migrations.CreateModel(
            name='MessageImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', yepes.fields.ImageField(upload_to=yepes.model_mixins.illustrated.image_upload_to, width_field='image_width', height_field='image_height', max_length=127, blank=True, verbose_name='Image')),
                ('image_height', yepes.fields.IntegerField(verbose_name='Image Height', min_value=0, null=True, editable=False, blank=True)),
                ('image_width', yepes.fields.IntegerField(verbose_name='Image Width', min_value=0, null=True, editable=False, blank=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('guid', yepes.fields.GuidField(charset='0123456789abcdef', editable=False, max_length=7, unique=True, verbose_name='Global Unique Identifier')),
                ('name', yepes.fields.IdentifierField(max_length=63, verbose_name='Name')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Message Image',
                'folder_name': 'newsletters',
                'verbose_name_plural': 'Message Images',
            },
        ),
        migrations.CreateModel(
            name='MessageLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('guid', yepes.fields.GuidField(charset='0123456789abcdef', editable=False, max_length=15, unique=True, verbose_name='Global Unique Identifier')),
                ('url', models.URLField(unique=True, max_length=255, verbose_name='URL')),
            ],
            options={
                'ordering': ['url'],
                'verbose_name': 'Message Link',
                'verbose_name_plural': 'Message Links',
            },
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', yepes.fields.CharField(verbose_name='Domain', unique=True, max_length=63, editable=False, validators=[django.core.validators.RegexValidator(re.compile('\n    \\A\n    (?:[A-Z0-9]+(?:-[A-Z0-9]+)*\\.)+\n    (?:[A-Z]{2,6})\n    \\Z\n', 66))])),
                ('is_trusted', yepes.fields.BooleanField(default=False, verbose_name='Is Trusted?')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'E-mail Domain',
                'verbose_name_plural': 'Domains',
            },
        ),
        migrations.CreateModel(
            name='SubscriberTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('name', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Name')),
                ('description', yepes.fields.TextField(verbose_name='Description', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Subscriber Tag',
                'verbose_name_plural': 'Subscriber Tags',
            },
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_enabled', models.BooleanField(default=True, verbose_name='Status', db_index=True, choices=[(True, 'Enabled'), (False, 'Disabled')])),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('guid', yepes.fields.GuidField(charset='0123456789abcdef', editable=False, max_length=31, unique=True, verbose_name='Global Unique Identifier')),
                ('email_address', yepes.fields.EmailField(unique=True, max_length=127, verbose_name='E-mail Address')),
                ('first_name', yepes.fields.CharField(max_length=63, verbose_name='First Name', blank=True)),
                ('last_name', yepes.fields.CharField(max_length=63, verbose_name='Last Name', blank=True)),
                ('score', yepes.fields.FloatField(default=2.0, verbose_name='Score', db_index=True, editable=False, blank=True)),
                ('email_domain', models.ForeignKey(related_name='subscribers', editable=False, to='newsletters.Domain', verbose_name='E-mail Domain')),
            ],
            options={
                'ordering': ['email_address'],
                'verbose_name': 'Subscriber',
                'verbose_name_plural': 'Subscribers',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('newsletter', models.ForeignKey(related_name='subscriptions', editable=False, to='newsletters.Newsletter', verbose_name='Newsletter')),
                ('subscriber', models.ForeignKey(related_name='subscriptions', editable=False, to='newsletters.Subscriber', verbose_name='Subscriber')),
                ('domain', models.ForeignKey(related_name='subscriptions', on_delete=django.db.models.deletion.SET_NULL, editable=False, to='newsletters.Domain', null=True, verbose_name='E-mail Domain')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Subscription Date')),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'Subscription',
                'verbose_name_plural': 'Subscriptions',
            },
        ),
        migrations.CreateModel(
            name='UnsubscriptionReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', yepes.fields.IntegerField(default=0, min_value=0, db_index=True, verbose_name='Index', blank=True)),
                ('description', yepes.fields.CharField(max_length=255, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Unsubscription Reason',
                'verbose_name_plural': 'Unsubscription Reasons',
            },
        ),
        migrations.CreateModel(
            name='Unsubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('newsletter', models.ForeignKey(related_name='unsubscriptions', editable=False, to='newsletters.Newsletter', verbose_name='Newsletter')),
                ('subscriber', models.ForeignKey(related_name='unsubscriptions', editable=False, to='newsletters.Subscriber', verbose_name='Subscriber')),
                ('domain', models.ForeignKey(related_name='unsubscriptions', on_delete=django.db.models.deletion.SET_NULL, editable=False, to='newsletters.Domain', null=True, verbose_name='E-mail Domain')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Unsubscribe Date')),
                ('reason', models.ForeignKey(related_name='unsubscriptions', editable=False, to='newsletters.UnsubscriptionReason', null=True, verbose_name='Unsubscription Reason')),
                ('last_message', models.ForeignKey(related_name='unsubscriptions', editable=False, to='newsletters.Message', null=True, verbose_name='Last Message')),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'Unsubscription',
                'verbose_name_plural': 'Unsubscriptions',
            },
        ),
        migrations.CreateModel(
            name='Bounce',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.ForeignKey(related_name='bounces', verbose_name='Message', to='newsletters.Message')),
                ('newsletter', models.ForeignKey(related_name='bounces', verbose_name='Newsletter', to='newsletters.Newsletter')),
                ('subscriber', models.ForeignKey(related_name='bounces', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Subscriber', to='newsletters.Subscriber', null=True)),
                ('domain', models.ForeignKey(related_name='bounces', on_delete=django.db.models.deletion.SET_NULL, verbose_name='E-mail Domain', to='newsletters.Domain', null=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Bounce Date')),
                ('header', yepes.fields.TextField(verbose_name='Header', blank=True)),
                ('body', yepes.fields.TextField(verbose_name='Body', blank=True)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'Bounce',
                'verbose_name_plural': 'Bounces',
            },
        ),
        migrations.CreateModel(
            name='Click',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link', models.ForeignKey(related_name='clicks', editable=False, to='newsletters.MessageLink', verbose_name='Message Link')),
                ('message', models.ForeignKey(related_name='clicks', editable=False, to='newsletters.Message', verbose_name='Message')),
                ('newsletter', models.ForeignKey(related_name='clicks', editable=False, to='newsletters.Newsletter', verbose_name='Newsletter')),
                ('subscriber', models.ForeignKey(related_name='clicks', on_delete=django.db.models.deletion.SET_NULL, editable=False, to='newsletters.Subscriber', null=True, verbose_name='Subscriber')),
                ('domain', models.ForeignKey(related_name='clicks', on_delete=django.db.models.deletion.SET_NULL, editable=False, to='newsletters.Domain', null=True, verbose_name='E-mail Domain')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Click Date')),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'Click',
                'verbose_name_plural': 'Clicks',
            },
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.ForeignKey(related_name='deliveries', editable=False, to='newsletters.Message', verbose_name='Message')),
                ('newsletter', models.ForeignKey(related_name='deliveries', editable=False, to='newsletters.Newsletter', verbose_name='Newsletter')),
                ('subscriber', models.ForeignKey(related_name='deliveries', editable=False, to='newsletters.Subscriber', verbose_name='Subscriber')),
                ('domain', models.ForeignKey(related_name='deliveries', editable=False, to='newsletters.Domain', verbose_name='E-mail Domain')),
                ('date', models.DateTimeField(verbose_name='Estimated Date', editable=False, db_index=True)),
                ('is_processed', yepes.fields.BooleanField(default=False, verbose_name='Is Processed?', db_index=True, editable=False)),
                ('process_date', models.DateTimeField(verbose_name='Effective Date', null=True, editable=False, blank=True)),
                ('is_bounced', yepes.fields.BooleanField(default=False, verbose_name='Is Bounced?', db_index=True, editable=False)),
                ('bounce_date', models.DateTimeField(verbose_name='Bounce Date', null=True, editable=False, blank=True)),
                ('is_opened', yepes.fields.BooleanField(default=False, verbose_name='Is Opened?', db_index=True, editable=False)),
                ('open_date', models.DateTimeField(verbose_name='Open Date', null=True, editable=False, blank=True)),
                ('is_clicked', yepes.fields.BooleanField(default=False, verbose_name='Is Clicked?', db_index=True, editable=False)),
                ('click_date', models.DateTimeField(verbose_name='Click Date', null=True, editable=False, blank=True)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'Delivery',
                'verbose_name_plural': 'Deliveries',
            },
        ),
        migrations.CreateModel(
            name='Open',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.ForeignKey(related_name='opens', editable=False, to='newsletters.Message', verbose_name='Message')),
                ('newsletter', models.ForeignKey(related_name='opens', editable=False, to='newsletters.Newsletter', verbose_name='Newsletter')),
                ('subscriber', models.ForeignKey(related_name='opens', on_delete=django.db.models.deletion.SET_NULL, editable=False, to='newsletters.Subscriber', null=True, verbose_name='Subscriber')),
                ('domain', models.ForeignKey(related_name='opens', on_delete=django.db.models.deletion.SET_NULL, editable=False, to='newsletters.Domain', null=True, verbose_name='E-mail Domain')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Open Date')),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'Open',
                'verbose_name_plural': 'Opens',
            },
        ),
        migrations.AddField(
            model_name='subscriber',
            name='newsletters',
            field=models.ManyToManyField(related_name='subscribers', verbose_name='Newsletters', through='newsletters.Subscription', to='newsletters.Newsletter'),
        ),
        migrations.AddField(
            model_name='subscriber',
            name='tags',
            field=models.ManyToManyField(related_name='subscribers', verbose_name='Tags', to='newsletters.SubscriberTag', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together=set([('newsletter', 'subscriber')]),
        ),
        migrations.AlterUniqueTogether(
            name='delivery',
            unique_together=set([('message', 'subscriber')]),
        ),
    ]
