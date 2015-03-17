# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0010_auto_20150316_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='email_last_instant',
            field=models.DateTimeField(verbose_name='Last Email Instant', default=None, blank=True, null=True),
            preserve_default=True,
        ),
    ]
