# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('monitor', '0038_auto_20150413_0912'),
    ]

    operations = [
        migrations.AddField(
            model_name='beer',
            name='beer_type',
            field=models.CharField(max_length=50, blank=True, verbose_name='Beer Type'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='bottle_count',
            field=models.PositiveSmallIntegerField(verbose_name='Bottle Count', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='bottle_notes',
            field=models.TextField(verbose_name='Bottle Notes', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='beer',
            name='brew_notes',
            field=models.TextField(verbose_name='Brew Notes', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='beer',
            name='brewer',
            field=models.ManyToManyField(db_constraint='Brewer/s', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='other_notes',
            field=models.TextField(verbose_name='Other Notes', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='beer',
            name='sugar_amount',
            field=models.CharField(max_length=30, blank=True, verbose_name='Amount of Sugar'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='config',
            name='temp_beer_dev',
            field=models.DecimalField(verbose_name='Beer Temp Deviation', decimal_places=2, default=None, null=True, max_digits=5, blank=True),
            preserve_default=True,
        ),
    ]
