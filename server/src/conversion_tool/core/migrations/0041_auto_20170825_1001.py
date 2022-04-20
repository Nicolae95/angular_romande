# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-08-25 08:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_translationrecords'),
    ]

    operations = [
        migrations.AddField(
            model_name='translationrecords',
            name='translated_year',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='translationrecords',
            name='year',
            field=models.TimeField(blank=True, null=True),
        ),
    ]