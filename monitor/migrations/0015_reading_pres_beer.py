# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0014_auto_20150318_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='reading',
            name='pres_beer',
            field=models.DecimalField(default=0, verbose_name='Beer Pressure', max_digits=5, decimal_places=2, blank=True),
            preserve_default=True,
        ),
    ]
