# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0012_config_email_timeout'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='read_last_instant',
            field=models.DateTimeField(blank=True, verbose_name='Last Reading Instant', null=True, default=None),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='config',
            name='read_missing',
            field=models.PositiveIntegerField(verbose_name='Missing Reading Warning (minutes)', default=0),
            preserve_default=True,
        ),
    ]
