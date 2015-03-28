# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0016_archive'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='archive',
            name='error_details',
        ),
        migrations.RemoveField(
            model_name='archive',
            name='error_flag',
        ),
        migrations.RemoveField(
            model_name='archive',
            name='temp_unit',
        ),
    ]
