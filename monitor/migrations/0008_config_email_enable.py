# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0007_reading_instant_actual'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='email_enable',
            field=models.BooleanField(verbose_name='Enable Email?', default=False),
            preserve_default=True,
        ),
    ]
