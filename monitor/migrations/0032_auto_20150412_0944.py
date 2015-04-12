# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0031_auto_20150406_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='beer',
            name='bottle_sg',
            field=models.DecimalField(blank=True, max_digits=4, verbose_name='Bottle SG', null=True, decimal_places=3),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='brew_sg',
            field=models.DecimalField(blank=True, max_digits=4, verbose_name='Brew SG', null=True, decimal_places=3),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='light_amb_mod',
            field=models.CharField(blank=True, verbose_name='Ambient Light Modifier', max_length=20),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='max_abv',
            field=models.DecimalField(blank=True, max_digits=2, verbose_name='Max ABV', null=True, decimal_places=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='pres_beer_mod',
            field=models.CharField(blank=True, verbose_name='Beer Pressure Modifier', max_length=20),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='pull_date',
            field=models.DateField(blank=True, verbose_name='Pull Date', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='temp_amb_mod',
            field=models.CharField(blank=True, verbose_name='Ambient Temp Modifier', max_length=20),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beer',
            name='temp_beer_mod',
            field=models.CharField(blank=True, verbose_name='Beer Temp Modifier', max_length=20),
            preserve_default=True,
        ),
    ]
