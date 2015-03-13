# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reading',
            name='instant_override',
            field=models.DateTimeField(null=True, default=None, blank=True),
            preserve_default=True,
        ),
    ]
