# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-05-28 11:34
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0009_auto_20180503_0907'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='token',
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True),
        ),
    ]