# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0027_auto_20150403_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='sensor',
            field=models.CharField(verbose_name='Sensor', max_length=50, choices=[('Temp Amb', 'Temp Amb'), ('Temp Beer', 'Temp Beer')], blank=True),
            preserve_default=True,
        ),
    ]
