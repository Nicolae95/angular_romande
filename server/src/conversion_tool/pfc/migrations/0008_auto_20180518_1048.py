# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-05-18 08:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pfc', '0007_auto_20180424_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='pfc',
            name='time',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='pfcmarket',
            name='time',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]