# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-08-13 14:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0024_profile_per_pag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='per_pag',
            field=models.IntegerField(blank=True, default=10, null=True),
        ),
    ]