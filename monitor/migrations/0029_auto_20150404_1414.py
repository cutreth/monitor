# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0028_event_sensor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='sensor',
            field=models.CharField(blank=True, choices=[('temp_amb', 'temp_amb'), ('temp_beer', 'temp_beer')], verbose_name='Sensor', max_length=50),
            preserve_default=True,
        ),
    ]
