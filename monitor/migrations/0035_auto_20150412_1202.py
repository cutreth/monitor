# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0034_auto_20150412_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='sensor',
            field=models.CharField(choices=[('temp_amb', 'temp_amb'), ('temp_beer', 'temp_beer')], null=True, max_length=50, blank=True, verbose_name='Sensor'),
            preserve_default=True,
        ),
    ]
