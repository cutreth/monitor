# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Beer',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('beer_text', models.CharField(max_length=30, verbose_name='Beer')),
                ('brew_date', models.DateField(null=True, verbose_name='Brew Date', blank=True)),
                ('bottle_date', models.DateField(null=True, verbose_name='Bottle Date', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('beer', models.ForeignKey(to='monitor.Beer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reading',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('instant', models.DateTimeField(auto_now_add=True)),
                ('temp_amb', models.DecimalField(max_digits=5, verbose_name='Ambient Temp', decimal_places=2)),
                ('temp_beer', models.DecimalField(max_digits=5, verbose_name='Beer Temp', decimal_places=2)),
                ('temp_unit', models.CharField(default='F', max_length=1, choices=[('F', 'Fahrenheit'), ('C', 'Celcius')], verbose_name='Temp Unit')),
                ('beer', models.ForeignKey(to='monitor.Beer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
