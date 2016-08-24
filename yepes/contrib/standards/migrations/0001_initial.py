# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import yepes.contrib.standards.model_mixins
import mptt.fields
import yepes.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', yepes.fields.CharField(help_text='You can find region names and United Nations codes here: <a target="_blank" href="http://en.wikipedia.org/wiki/UN_M.49">http://en.wikipedia.org/wiki/UN_M.49</a>', unique=True, max_length=127, verbose_name='Native Name')),
                ('name_de', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='German Name', blank=True)),
                ('name_en', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='English Name', blank=True)),
                ('name_es', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Spanish Name', blank=True)),
                ('name_fr', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='French Name', blank=True)),
                ('name_pt', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Portuguese Name', blank=True)),
                ('name_ru', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Russian Name', blank=True)),
                ('name_zh', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Chinese Name', blank=True)),
                ('number', yepes.fields.CharField(min_length=3, charset='0-9', max_length=3, help_text='Specify numeric region code, for example "150".', unique=True, verbose_name='Number')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='Parent Region', to='standards.Region', null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Supranational Region',
                'verbose_name_plural': 'Supranational Regions',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_enabled', models.BooleanField(default=True, verbose_name='Status', db_index=True, choices=[(True, 'Enabled'), (False, 'Disabled')])),
                ('name', yepes.fields.CharField(help_text='You can find country names and ISO codes here: <a target="_blank" href="http://en.wikipedia.org/wiki/ISO_3166-1">http://en.wikipedia.org/wiki/ISO_3166-1</a>', unique=True, max_length=127, verbose_name='Native Name')),
                ('name_de', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='German Name', blank=True)),
                ('name_en', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='English Name', blank=True)),
                ('name_es', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Spanish Name', blank=True)),
                ('name_fr', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='French Name', blank=True)),
                ('name_pt', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Portuguese Name', blank=True)),
                ('name_ru', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Russian Name', blank=True)),
                ('name_zh', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Chinese Name', blank=True)),
                ('region', models.ForeignKey(related_name='countries', verbose_name='Region', to='standards.Region')),
                ('code', yepes.fields.CharField(min_length=2, force_upper=True, charset='A-Z', max_length=2, help_text='Specify 2-letter country code, for example "ES".', unique=True, verbose_name='Code')),
                ('long_code', yepes.fields.CharField(min_length=3, force_upper=True, charset='A-Z', max_length=3, help_text='Specify 3-letter country code, for example "ESP".', unique=True, verbose_name='Long Code')),
                ('number', yepes.fields.CharField(min_length=3, charset='0-9', max_length=3, help_text='Specify numeric country code, for example "724".', unique=True, verbose_name='Number')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='CountrySubdivision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_enabled', models.BooleanField(default=True, verbose_name='Status', db_index=True, choices=[(True, 'Enabled'), (False, 'Disabled')])),
                ('name', yepes.fields.CharField(unique=True, max_length=127, verbose_name='Native Name')),
                ('name_de', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='German Name', blank=True)),
                ('name_en', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='English Name', blank=True)),
                ('name_es', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Spanish Name', blank=True)),
                ('name_fr', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='French Name', blank=True)),
                ('name_pt', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Portuguese Name', blank=True)),
                ('name_ru', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Russian Name', blank=True)),
                ('name_zh', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Chinese Name', blank=True)),
                ('code', yepes.fields.CharField(min_length=4, force_upper=True, charset='A-Z0-9\\-', max_length=6, help_text='Specify country subdivision code, for example "ES-O".', unique=True, verbose_name='Code')),
                ('country', models.ForeignKey(related_name='subdivisions', verbose_name='Country', to='standards.Country')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Country Subdivision',
                'verbose_name_plural': 'Country Subdivisions',
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_enabled', models.BooleanField(default=True, verbose_name='Status', db_index=True, choices=[(True, 'Enabled'), (False, 'Disabled')])),
                ('name', yepes.fields.CharField(help_text='You can find currency names and ISO codes here: <a target="_blank" href="http://en.wikipedia.org/wiki/ISO_4217">http://en.wikipedia.org/wiki/ISO_4217</a>', unique=True, max_length=127, verbose_name='Native Name')),
                ('name_de', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='German Name', blank=True)),
                ('name_en', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='English Name', blank=True)),
                ('name_es', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Spanish Name', blank=True)),
                ('name_fr', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='French Name', blank=True)),
                ('name_pt', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Portuguese Name', blank=True)),
                ('name_ru', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Russian Name', blank=True)),
                ('name_zh', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Chinese Name', blank=True)),
                ('symbol', yepes.fields.CharField(help_text='Specify currency symbol, for example "\u20ac".', force_upper=True, max_length=7, verbose_name='Symbol', db_index=True)),
                ('code', yepes.fields.CharField(min_length=3, force_upper=True, charset='A-Z', max_length=3, help_text='Specify 3-letter currency code, for example "EUR".', unique=True, verbose_name='Code')),
                ('number', yepes.fields.CharField(min_length=3, charset='0-9', max_length=3, help_text='Specify numeric currency code, for example "978".', unique=True, verbose_name='Number')),
                ('decimals', yepes.fields.SmallIntegerField(default=2, help_text='Number of digits after the decimal separator.', min_value=0, verbose_name='Decimals', max_value=6)),
                ('countries', models.ManyToManyField(help_text='Countries using this currency.', related_name='currencies', verbose_name='Countries', to='standards.Country', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Currency',
                'verbose_name_plural': 'Currencies',
            },
        ),
        migrations.CreateModel(
            name='GeographicArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('name', yepes.fields.CharField(unique=True, max_length=127, verbose_name='Native Name')),
                ('name_de', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='German Name', blank=True)),
                ('name_en', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='English Name', blank=True)),
                ('name_es', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Spanish Name', blank=True)),
                ('name_fr', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='French Name', blank=True)),
                ('name_pt', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Portuguese Name', blank=True)),
                ('name_ru', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Russian Name', blank=True)),
                ('name_zh', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Chinese Name', blank=True)),
                ('api_id', yepes.fields.IdentifierField(verbose_name='API Id')),
                ('description', yepes.fields.TextField(verbose_name='Description', blank=True)),
                ('excluded_countries', models.ManyToManyField(related_name='areas_that_exclude_it', verbose_name='Excluded Countries', to='standards.Country', blank=True)),
                ('excluded_subdivisions', models.ManyToManyField(related_name='areas_that_exclude_it', verbose_name='Excluded Subdivisions', to='standards.CountrySubdivision', blank=True)),
                ('included_countries', models.ManyToManyField(related_name='areas_that_include_it', verbose_name='Included Countries', to='standards.Country', blank=True)),
                ('included_subdivisions', models.ManyToManyField(related_name='areas_that_include_it', verbose_name='Included Subdivisions', to='standards.CountrySubdivision', blank=True)),
            ],
            options={
                'verbose_name': 'Geographic Area',
                'verbose_name_plural': 'Geographic Areas',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_enabled', models.BooleanField(default=True, verbose_name='Status', db_index=True, choices=[(True, 'Enabled'), (False, 'Disabled')])),
                ('name', yepes.fields.CharField(help_text='You can find language names and ISO codes here: <a target="_blank" href="http://en.wikipedia.org/wiki/List_of_ISO_639-3_codes">http://en.wikipedia.org/wiki/List_of_ISO_639-3_codes</a>', unique=True, max_length=127, verbose_name='Native Name')),
                ('name_de', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='German Name', blank=True)),
                ('name_en', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='English Name', blank=True)),
                ('name_es', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Spanish Name', blank=True)),
                ('name_fr', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='French Name', blank=True)),
                ('name_pt', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Portuguese Name', blank=True)),
                ('name_ru', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Russian Name', blank=True)),
                ('name_zh', yepes.contrib.standards.model_mixins.LocalizedNameField(db_index=True, max_length=127, verbose_name='Chinese Name', blank=True)),
                ('tag', yepes.fields.CharField(min_length=2, charset='a-z', force_lower=True, max_length=3, help_text='You can find an explanation about the language tags here: <a target="_blank" href="http://www.w3.org/International/articles/language-tags/Overview.en.php">http://www.w3.org/International/articles/language-tags/Overview.en.php</a>', unique=True, verbose_name='Tag')),
                ('iso_639_1', yepes.fields.CharField(min_length=2, charset='a-z', force_lower=True, max_length=2, blank=True, help_text='Specify 2-letter language code, for example "es".', verbose_name='ISO 639-1', db_index=True)),
                ('iso_639_2', yepes.fields.CharField(min_length=3, charset='a-z', force_lower=True, max_length=3, blank=True, help_text='Specify 3-letter language code, for example "spa".', verbose_name='ISO 639-2', db_index=True)),
                ('iso_639_3', yepes.fields.CharField(min_length=3, charset='a-z', force_lower=True, max_length=3, blank=True, help_text='Specify 3-letter language code, for example "spa".', verbose_name='ISO 639-3', db_index=True)),
                ('countries', models.ManyToManyField(help_text='Countries where this language is official.', related_name='languages', verbose_name='Countries', to='standards.Country', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Language',
                'verbose_name_plural': 'Languages',
            },
        ),
    ]
