from itertools import chain , groupby
from collections import defaultdict
from operator import itemgetter
from django.db import models
from core.models import *
from pfc.models import *
import numpy as np
import csv
import pytz
from pytz import country_timezones
from logic.upload_data import upload_pondere

class ProfileTypePondere(models.Model):
    name = models.CharField(blank=True, max_length=100)
    year = models.IntegerField(blank=True, null=True)
    data_file = models.FileField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            super(ProfileTypePondere, self).save(*args, **kwargs)
            self.process_file(self.data_file.file)
        super(ProfileTypePondere, self).save(*args, **kwargs)

    @transaction.atomic
    def process_file(self, data_file):
        cet = pytz.timezone('CET')
        fileName, fileExtension = os.path.splitext(data_file.name)
        if fileExtension.lower() == '.xlsx' or fileExtension.lower() == '.xls':
            upload_pondere(self, data_file)
        else:
            print 'Error'


class ProfileTypePondereConsumptionRecord(TimeStampedModel):
    profile = models.ForeignKey(ProfileTypePondere)
    value = models.FloatField()
    interval_start = models.DateTimeField()
    interval = models.DurationField()

    def __unicode__(self):
        return str(self.value)
