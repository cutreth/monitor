# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0011_config_email_last_instant'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='email_timeout',
            field=models.PositiveIntegerField(verbose_name='Email Timeout (minutes)', default=60),
            preserve_default=True,
        ),
    ]
