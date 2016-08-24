# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import yepes.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    initial = True

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date')),
                ('last_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('key', yepes.fields.IdentifierField(max_length=63, verbose_name='Key')),
                ('width', yepes.fields.IntegerField(default=0, min_value=0, verbose_name='Width')),
                ('height', yepes.fields.IntegerField(default=0, min_value=0, verbose_name='Height')),
                ('background', yepes.fields.ColorField(blank=True, null=True, verbose_name='Background')),
                ('mode', yepes.fields.CharField(default='limit', max_length=15, verbose_name='Crop Mode', choices=[('scale', 'Scale'), ('fit', 'Fit'), ('limit', 'Fit without enlarging'), ('fill', 'Fill'), ('lfill', 'Fill without enlarging'), ('pad', 'Pad'), ('lpad', 'Pad without enlarging'), ('crop', 'Crop')])),
                ('algorithm', yepes.fields.CharField(default='undefined', max_length=15, verbose_name='Resizing Algorithm', choices=[('undefined', 'undefined'), ('sample', 'sample'), ('liquid', 'liquid'), ('point', 'point'), ('box', 'box'), ('triangle', 'triangle'), ('hermite', 'hermite'), ('hanning', 'hanning'), ('hamming', 'hamming'), ('blackman', 'blackman'), ('gaussian', 'gaussian'), ('quadratic', 'quadratic'), ('cubic', 'cubic'), ('catrom', 'catrom'), ('mitchell', 'mitchell'), ('jinc', 'jinc'), ('sinc', 'sinc'), ('sincfast', 'sincfast'), ('kaiser', 'kaiser'), ('welsh', 'welsh'), ('parzen', 'parzen'), ('bohman', 'bohman'), ('bartlett', 'bartlett'), ('lagrange', 'lagrange'), ('lanczos', 'lanczos'), ('lanczossharp', 'lanczossharp'), ('lanczos2', 'lanczos2'), ('lanczos2sharp', 'lanczos2sharp'), ('robidoux', 'robidoux'), ('robidouxsharp', 'robidouxsharp'), ('cosine', 'cosine'), ('spline', 'spline'), ('sentinel', 'sentinel')])),
                ('gravity', yepes.fields.CharField(default='center', max_length=15, verbose_name='Gravity', choices=[('north_west', 'Northwest'), ('north', 'North'), ('north_east', 'Northeast'), ('west', 'West'), ('center', 'Center'), ('east', 'East'), ('south_west', 'Southwest'), ('south', 'South'), ('south_east', 'Southeast')])),
                ('format', yepes.fields.CharField(default='JPEG', max_length=15, verbose_name='Format', choices=[('GIF', 'GIF'), ('JPEG', 'JPEG'), ('PNG8', 'PNG8'), ('PNG64', 'PNG64'), ('WEBP', 'WEBP')])),
                ('quality', yepes.fields.IntegerField(default=85, max_value=100, min_value=1, verbose_name='Quality')),
            ],
            options={
                'ordering': ['key'],
                'verbose_name': 'Thumbnail Configuration',
                'verbose_name_plural': 'Configurations',
            },
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', yepes.fields.CharField(unique=True, max_length=255, verbose_name='Name')),
                ('last_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last Modified')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Source',
                'verbose_name_plural': 'Sources',
            },
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', yepes.fields.CharField(max_length=255, verbose_name='Name')),
                ('last_modified', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last Modified')),
                ('source', models.ForeignKey(related_name='thumbnails', verbose_name='Source', to='thumbnails.Source')),
            ],
            options={
                'ordering': ['source', 'name'],
                'verbose_name': 'Thumbnail',
                'verbose_name_plural': 'Thumbnails',
            },
        ),
        migrations.AlterUniqueTogether(
            name='thumbnail',
            unique_together=set([('source', 'name')]),
        ),
    ]
