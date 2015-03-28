# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0019_auto_20150328_1431'),
    ]

    operations = [
        migrations.RenameField(
            model_name='archive',
            old_name='brew_date',
            new_name='reading_date',
        ),
    ]
