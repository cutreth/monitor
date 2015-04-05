# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0029_auto_20150404_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='reading',
            name='event_temp_amb',
            field=models.ForeignKey(to='monitor.Event', blank=True, null=True, related_name='reading_to_temp_amb'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reading',
            name='event_temp_beer',
            field=models.ForeignKey(to='monitor.Event', blank=True, null=True, related_name='reading_to_temp_beer'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='reading',
            field=models.ForeignKey(to='monitor.Reading', blank=True, null=True, related_name='event_to_reading'),
            preserve_default=True,
        ),
    ]
