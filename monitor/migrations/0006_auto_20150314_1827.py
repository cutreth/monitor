# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0005_auto_20150314_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reading',
            name='error_details',
            field=models.CharField(verbose_name='Error Details', max_length=150, blank=True),
            preserve_default=True,
        ),
    ]
