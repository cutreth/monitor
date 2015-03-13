# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0002_reading_instant_override'),
    ]

    operations = [
        migrations.AddField(
            model_name='reading',
            name='light_amb',
            field=models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Ambient Light', blank=True, default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reading',
            name='instant',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Instant'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reading',
            name='instant_override',
            field=models.DateTimeField(verbose_name='Instant Override', blank=True, null=True, default=None),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reading',
            name='temp_amb',
            field=models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Ambient Temp', blank=True, default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reading',
            name='temp_beer',
            field=models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Beer Temp', blank=True, default=0),
            preserve_default=True,
        ),
    ]
