# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0036_auto_20150413_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beer',
            name='max_abv',
            field=models.DecimalField(decimal_places=2, null=True, verbose_name='Max ABV', max_digits=2, blank=True),
            preserve_default=True,
        ),
    ]
