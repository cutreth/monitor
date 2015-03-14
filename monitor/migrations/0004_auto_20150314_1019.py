# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0003_auto_20150313_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='temp_amb_base',
            field=models.DecimalField(max_digits=5, default=None, decimal_places=2, blank=True, verbose_name='Ambient Temp Baseline', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='config',
            name='temp_amb_dev',
            field=models.DecimalField(max_digits=5, default=None, decimal_places=2, blank=True, verbose_name='Ambient Temp Deviation', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='config',
            name='temp_beer_base',
            field=models.DecimalField(max_digits=5, default=None, decimal_places=2, blank=True, verbose_name='Beer Temp Baseline', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='config',
            name='temp_beer_dev',
            field=models.DecimalField(max_digits=5, default=None, decimal_places=2, blank=True, verbose_name='Ambient Temp Deviation', null=True),
            preserve_default=True,
        ),
    ]
