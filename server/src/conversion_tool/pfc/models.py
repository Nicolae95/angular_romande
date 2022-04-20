from __future__ import unicode_literals
from datetime import datetime, timedelta, time
from django.db import models
from model_utils.models import TimeStampedModel
from django.db import transaction
import csv
import os
import pytz
from pytz import country_timezones

from logic.upload.pfc import *
from logic.upload.pfc_market import *


class PFC(models.Model):
    pfc_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created = models.DateTimeField(default=datetime.now, blank=True)
    time = models.CharField(max_length=100, null=True, blank=True)
    file = models.CharField(max_length=255, null=True, blank=True)
    risc = models.CharField(max_length=255, null=True, blank=True)
    eco = models.CharField(max_length=255, null=True, blank=True)


    def __unicode__(self):
        return '{}'.format(self.pfc_id)

    class Meta:
        ordering = ('-pk',)


class PFCMarket(models.Model):
    pfc_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created = models.DateTimeField(default=datetime.now, blank=True)
    time = models.CharField(max_length=100, null=True, blank=True)
    offer = models.IntegerField(blank=True, null=True)
    opportunite = models.CharField(max_length=255, null=True, blank=True)
    custom = models.CharField(max_length=255, null=True, blank=True)
    file = models.CharField(max_length=255, null=True, blank=True)
    risc = models.CharField(max_length=255, null=True, blank=True)
    eco = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return '{}'.format(self.pfc_id)

    class Meta:
        ordering = ('-pk',)


class PfcConsumptionFile(TimeStampedModel):
    pfc = models.ForeignKey(PFC, null=True, blank=True)
    pfc_market = models.ForeignKey(PFCMarket, null=True, blank=True)
    data_file = models.FileField()

    def __unicode__(self):
        return self.data_file.name

    def save(self, *args, **kwargs):
        if not self.pk:
            super(PfcConsumptionFile, self).save(*args, **kwargs)
            self.process_file(self.data_file.file)
        super(PfcConsumptionFile, self).save(*args, **kwargs)


    @transaction.atomic
    def process_file(self, data_file):
        cet = pytz.timezone('CET')
        parse = False
        fileName, fileExtension = os.path.splitext(data_file.name)
        print self.pfc, self.pfc_market
        if (fileExtension.lower() == '.xlsx' or fileExtension.lower() == '.xls') and self.pfc:
            upload_pfc_xls(self.id, self.pfc, data_file)
        elif fileExtension.lower() == '.csv' and self.pfc:
            upload_pfc_csv(self.id, self.pfc, data_file)
        elif fileExtension.lower() == '.csv' and self.pfc_market:
            upload_pfc_csv_market(self.id, self.pfc_market, data_file)
        elif (fileExtension.lower() == '.xlsx' or fileExtension.lower() == '.xls') and self.pfc_market:
            upload_pfc_xls_market(self.id, self.pfc_market, data_file)
        else:
            return 'Error'


class PfcConsumptionRecord(TimeStampedModel):
    from_file = models.ForeignKey(PfcConsumptionFile, null=True, blank=True)
    pfc = models.ForeignKey(PFC)
    value = models.FloatField()
    unit = models.CharField(max_length=255)
    interval_start = models.DateTimeField()
    interval = models.DurationField()

    class Meta:
        ordering = ('-interval_start',)

    def __unicode__(self):
        return '{}: {} {} from file {}'.format(
            self.interval_start, self.value, self.unit, self.from_file_id)


class PfcMarketConsumptionRecord(TimeStampedModel):
    from_file = models.ForeignKey(PfcConsumptionFile, null=True, blank=True)
    pfc_market = models.ForeignKey(PFCMarket)
    value = models.FloatField()
    unit = models.CharField(max_length=255)
    interval_start = models.DateTimeField()
    interval = models.DurationField()

    class Meta:
        ordering = ('-interval_start',)

    def __unicode__(self):
        return '{}: {} {} from file {}'.format(
            self.interval_start, self.value, self.unit, self.from_file_id)


class PfcPeakRecord(TimeStampedModel):
    PEAK_CHOICES = (
        ('peak', 'Peak'),
        ('base', 'Base'),
    )
    pfc = models.ForeignKey(PFC)
    value = models.FloatField()
    unit = models.CharField(max_length=255, null=True, blank=True)
    peak = models.CharField(max_length=10, choices=PEAK_CHOICES, null=True, blank=True)
    year = models.IntegerField()

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}: {} {} from year {}'.format(self.pfc, self.value, self.peak, self.year)
