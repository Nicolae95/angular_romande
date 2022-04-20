# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-06-19 12:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0007_location_holidays'),
    ]

    operations = [
        migrations.CreateModel(
            name='HolidayFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_file', models.FileField(upload_to=b'')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='geo.Region')),
            ],
        ),
    ]