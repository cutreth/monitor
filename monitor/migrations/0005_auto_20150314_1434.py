# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0004_auto_20150314_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='reading',
            name='error_details',
            field=models.SlugField(verbose_name='Error Details', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reading',
            name='error_flag',
            field=models.NullBooleanField(verbose_name='Error?'),
            preserve_default=True,
        ),
    ]
