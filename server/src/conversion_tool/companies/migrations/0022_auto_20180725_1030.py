# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-07-25 07:30
from __future__ import unicode_literals

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0021_auto_20180724_1742'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientlog',
            name='location',
        ),
        migrations.AddField(
            model_name='clientlog',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='clientlog',
            name='country',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
    ]