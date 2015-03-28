# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0015_reading_pres_beer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Archive',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('instant_actual', models.TextField(verbose_name='Instant Actual')),
                ('light_amb', models.TextField(verbose_name='Ambient Light')),
                ('pres_beer', models.TextField(verbose_name='Beer Pressure')),
                ('temp_amb', models.TextField(verbose_name='Ambient Temp')),
                ('temp_beer', models.TextField(verbose_name='Beer Temp')),
                ('temp_unit', models.TextField(verbose_name='Temp Unit')),
                ('error_flag', models.TextField(verbose_name='Error?')),
                ('error_details', models.TextField(verbose_name='Error Details')),
                ('count', models.PositiveIntegerField(verbose_name='Count', default=0)),
                ('beer', models.ForeignKey(to='monitor.Beer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
