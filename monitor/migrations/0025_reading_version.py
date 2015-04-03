# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0024_auto_20150401_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='reading',
            name='version',
            field=models.PositiveIntegerField(default=1, verbose_name='Version'),
            preserve_default=True,
        ),
    ]
