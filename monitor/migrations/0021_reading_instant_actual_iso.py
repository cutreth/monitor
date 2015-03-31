# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0020_auto_20150328_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='reading',
            name='instant_actual_iso',
            field=models.SlugField(default=None, null=True, verbose_name='Instant Actual (ISO)', blank=True),
            preserve_default=True,
        ),
    ]
