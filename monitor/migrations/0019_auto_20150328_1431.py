# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0018_archive_brew_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archive',
            name='brew_date',
            field=models.DateField(default=datetime.datetime(2015, 3, 28, 14, 31, 30, 115660), verbose_name='Reading Date'),
            preserve_default=False,
        ),
    ]
