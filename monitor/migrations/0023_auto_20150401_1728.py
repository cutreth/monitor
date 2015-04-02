# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0022_auto_20150401_0706'),
    ]

    operations = [
        migrations.AddField(
            model_name='archive',
            name='update_instant',
            field=models.DateTimeField(blank=True, default=None, verbose_name='Last Updated', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='archive',
            name='reading_date',
            field=models.DateField(db_index=True, verbose_name='Reading Date'),
            preserve_default=True,
        ),
    ]
