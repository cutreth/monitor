# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0017_auto_20150328_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='archive',
            name='brew_date',
            field=models.DateField(verbose_name='Reading Date', blank=True, null=True),
            preserve_default=True,
        ),
    ]
