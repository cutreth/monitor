# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0030_auto_20150405_0949'),
    ]

    operations = [
        migrations.AddField(
            model_name='archive',
            name='event_temp_amb',
            field=models.TextField(verbose_name='Amb Temp Events', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='archive',
            name='event_temp_beer',
            field=models.TextField(verbose_name='Beer Temp Events', default=''),
            preserve_default=False,
        ),
    ]
