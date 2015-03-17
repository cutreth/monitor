# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0009_auto_20150316_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='email_api_key',
            field=models.CharField(max_length=50, verbose_name='API Key', blank=True, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='config',
            name='email_sender',
            field=models.CharField(max_length=50, verbose_name='From', blank=True, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='config',
            name='email_subject',
            field=models.CharField(max_length=50, verbose_name='Subject', blank=True, default=''),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='config',
            name='email_to',
            field=models.CharField(max_length=50, verbose_name='To', blank=True, default=''),
            preserve_default=True,
        ),
    ]
