# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0008_config_email_enable'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='email_api_key',
            field=models.SlugField(verbose_name='API Key', default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='config',
            name='email_sender',
            field=models.SlugField(verbose_name='From', default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='config',
            name='email_subject',
            field=models.SlugField(verbose_name='Subject', default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='config',
            name='email_to',
            field=models.SlugField(verbose_name='To', default=''),
            preserve_default=True,
        ),
    ]
