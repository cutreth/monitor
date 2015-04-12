# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0033_auto_20150412_1048'),
    ]

    operations = [
        migrations.AddField(
            model_name='archive',
            name='light_amb_orig',
            field=models.TextField(default='', verbose_name='Original Ambient Light'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='archive',
            name='pres_beer_orig',
            field=models.TextField(default='', verbose_name='Original Beer Pressure'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='archive',
            name='temp_amb_orig',
            field=models.TextField(default='', verbose_name='Original Ambient Temp'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='archive',
            name='temp_beer_orig',
            field=models.TextField(default='', verbose_name='Original Beer Temp'),
            preserve_default=False,
        ),
    ]
