# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0037_auto_20150413_0910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beer',
            name='max_abv',
            field=models.DecimalField(verbose_name='Max ABV', blank=True, decimal_places=2, max_digits=3, null=True),
            preserve_default=True,
        ),
    ]
