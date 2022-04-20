# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-05-03 08:08
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0037_offer_unique_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='unique_id',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]