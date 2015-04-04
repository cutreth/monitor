# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0025_reading_version'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('instant', models.DateTimeField(auto_now_add=True, verbose_name='Instant')),
                ('category', models.CharField(max_length=50, choices=[('Bounds', 'Bounds'), ('Missing', 'Bounds')], verbose_name='Category')),
                ('details', models.CharField(max_length=150, verbose_name='Error Details', blank=True)),
                ('beer', models.ForeignKey(to='monitor.Beer')),
                ('reading', models.ForeignKey(to='monitor.Reading')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='reading',
            name='version',
            field=models.PositiveIntegerField(default=0, verbose_name='Version'),
            preserve_default=True,
        ),
    ]
