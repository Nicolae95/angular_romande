# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-08-02 09:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_weekday'),
    ]

    operations = [
        migrations.AddField(
            model_name='shedule',
            name='weekdays',
            field=models.ManyToManyField(to='core.Weekday'),
        ),
        migrations.AlterField(
            model_name='shedule',
            name='hours',
            field=models.ManyToManyField(to='core.Hour'),
        ),
        migrations.AlterField(
            model_name='shedule',
            name='months',
            field=models.ManyToManyField(to='core.Months'),
        ),
    ]