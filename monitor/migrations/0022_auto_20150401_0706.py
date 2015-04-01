# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0021_reading_instant_actual_iso'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='api_prod_key',
            field=models.CharField(verbose_name='Prod API Key', max_length=50, default='', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='config',
            name='api_server_url',
            field=models.CharField(verbose_name='Server URL', max_length=50, default='', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='config',
            name='api_test_key',
            field=models.CharField(verbose_name='Test API Key', max_length=50, default='', blank=True),
            preserve_default=True,
        ),
    ]
