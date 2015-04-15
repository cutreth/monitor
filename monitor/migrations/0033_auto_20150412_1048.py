# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0032_auto_20150412_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='reading',
            name='light_amb_orig',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, verbose_name='Original Ambient Light', default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reading',
            name='pres_beer_orig',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, verbose_name='Original Beer Pressure', default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reading',
            name='temp_amb_orig',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, verbose_name='Original Ambient Temp', default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reading',
            name='temp_beer_orig',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, verbose_name='Original Beer Temp', default=0),
            preserve_default=True,
        ),
    ]
