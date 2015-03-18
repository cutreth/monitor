# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0013_auto_20150317_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='email_subject',
            field=models.CharField(max_length=150, verbose_name='Subject', blank=True, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='config',
            name='email_to',
            field=models.CharField(max_length=150, verbose_name='To', blank=True, default=''),
            preserve_default=True,
        ),
    ]
