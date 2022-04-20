# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.apps import apps
from django.db import models, transaction
from django_countries.fields import CountryField
from utils.holiday_import import upload_holidays 
from xlrd import open_workbook, xldate
import csv
import pytz
import os
# Create your models here.


class Location(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    country = CountryField()
    region = models.ForeignKey('Region', null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    holidays = models.ManyToManyField('Holiday')

    def __unicode__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=255)
    country = CountryField()


class Holiday(models.Model):
    # MONTH_CHOICES = (
    #     (1, 'January'),
    #     (2, 'February'),
    #     (3, 'March'),
    #     (4, 'April'),
    #     (5, 'May'),
    #     (6, 'June'),
    #     (7, 'July'),
    #     (8, 'August'),
    #     (9, 'September'),
    #     (10, 'October'),
    #     (11, 'November'),
    #     (12, 'December')
    # )
    title = models.CharField(max_length=255)
    # month = models.SmallIntegerField(choices=MONTH_CHOICES, default=1)
    # day = models.SmallIntegerField(default=1)
    date = models.DateField()
    country = CountryField()
    region = models.ForeignKey(Region, null=True, blank=True)

    def __unicode__(self):
        # return '{} {}: {} in {}'.format(self.get_month_display(), self.day, self.title, self.country.name)
        return '{}: {} in {}'.format(self.date, self.title, self.country.name)


class HolidayFile(models.Model):
    region = models.ForeignKey(Region, null=True, blank=True)
    data_file = models.FileField()

    def __unicode__(self):
        return self.data_file.name

    def save(self, *args, **kwargs):
        if not self.pk:
            super(HolidayFile, self).save(*args, **kwargs)
            self.process_file()
        super(HolidayFile, self).save(*args, **kwargs)

    @transaction.atomic
    def process_file(self):
        cet = pytz.timezone('UTC')
        parse = False
        print self.data_file.file
        fileName, fileExtension = os.path.splitext(self.data_file.file.name)
        print fileName, fileExtension
        if fileExtension.lower() == '.csv':
            upload_holidays(self, self.data_file.file)
        else:
            'error'
