# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0026_auto_20150403_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='category',
            field=models.CharField(max_length=50, choices=[('Bounds', 'Bounds'), ('Missing', 'Missing')], verbose_name='Category'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='reading',
            field=models.ForeignKey(to='monitor.Reading', blank=True, null=True),
            preserve_default=True,
        ),
    ]
