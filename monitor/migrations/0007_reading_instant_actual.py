# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0006_auto_20150314_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='reading',
            name='instant_actual',
            field=models.DateTimeField(verbose_name='Instant Actual', default=None, blank=True, null=True),
            preserve_default=True,
        ),
    ]
