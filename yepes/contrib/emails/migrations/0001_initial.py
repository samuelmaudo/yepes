# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import yepes.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('name', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Name')),
                ('host', yepes.fields.CharField(help_text='Address of the SMTP server.', max_length=255, verbose_name='Host')),
                ('port', yepes.fields.IntegerField(default=25, min_value=0, verbose_name='Port')),
                ('username', yepes.fields.CharField(max_length=255, verbose_name='Username')),
                ('password', yepes.fields.EncryptedCharField(max_length=255, verbose_name='Password')),
                ('is_secure', yepes.fields.BooleanField(default=False, help_text='Whether to use a secure connection when talking to the SMTP server.', verbose_name='Use TLS?')),
                ('is_logged', yepes.fields.BooleanField(default=False, help_text='Whether to store a copy of each sent mail.', verbose_name='Store Mails?')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'E-mail Connection',
                'verbose_name_plural': 'Connections',
            },
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('sender', yepes.fields.CharField(max_length=255, verbose_name='Sender')),
                ('recipients', yepes.fields.TextField(verbose_name='Recipients', blank=True)),
                ('other_recipients', yepes.fields.TextField(verbose_name='Other Recipients', blank=True)),
                ('hidden_recipients', yepes.fields.TextField(verbose_name='Hidden Recipients', blank=True)),
                ('subject', yepes.fields.CharField(max_length=255, verbose_name='Subject', blank=True)),
                ('html', yepes.fields.TextField(verbose_name='HTML Version', blank=True)),
                ('text', yepes.fields.TextField(verbose_name='Plain Text Version', blank=True)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'Delivery',
                'verbose_name_plural': 'Deliveries',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('name', yepes.fields.CharField(unique=True, max_length=63, verbose_name='Name')),
                ('sender_name', yepes.fields.CharField(max_length=127, verbose_name="Sender's Name")),
                ('sender_address', yepes.fields.CharField(max_length=127, verbose_name="Sender's Address")),
                ('recipient_name', yepes.fields.CharField(max_length=255, verbose_name="Recipient's Name", blank=True)),
                ('recipient_address', yepes.fields.CharField(help_text='If field is blank, it will be populated when the message is sent.', max_length=255, verbose_name="Recipient's Address", blank=True)),
                ('reply_to_name', yepes.fields.CharField(max_length=127, verbose_name='Reply To Name', blank=True)),
                ('reply_to_address', yepes.fields.CharField(max_length=127, verbose_name='Reply To Address', blank=True)),
                ('subject', yepes.fields.CharField(max_length=255, verbose_name='Subject')),
                ('html', yepes.fields.TextField(verbose_name='HTML Version')),
                ('text', yepes.fields.TextField(verbose_name='Plain Text Version', blank=True)),
                ('connection', yepes.fields.CachedForeignKey(related_name='messages', verbose_name='Connection', to='emails.Connection')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
        ),
    ]
