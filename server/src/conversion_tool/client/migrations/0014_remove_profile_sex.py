# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-14 06:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0013_auto_20180613_1135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='sex',
        ),
    ]