# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0035_auto_20150412_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='beer',
            name='bottle_temp',
            field=models.DecimalField(decimal_places=1, verbose_name='Bottle Temp', null=True, blank=True, max_digits=3),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='brew_temp',
            field=models.DecimalField(decimal_places=1, verbose_name='Brew Temp', null=True, blank=True, max_digits=3),
            preserve_default=True,
        ),
    ]
