# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0023_auto_20150401_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='archive_key',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='config',
            name='reading_key',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
