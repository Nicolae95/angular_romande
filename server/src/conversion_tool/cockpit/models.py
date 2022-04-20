from itertools import chain, groupby
from collections import defaultdict
from operator import itemgetter
from django.db import models
from core.models import *
from pfc.models import *
from offers.models import *
import numpy as np
import csv
import pytz
from pytz import country_timezones


class CockpitNews(models.Model):
    name = models.CharField(blank=True, max_length=100)
    email_name = models.CharField(blank=True, max_length=100)
    clients = models.ManyToManyField('companies.Company', blank=True,
                                     related_name='cockpit_company')
    offers = models.ManyToManyField('offers.Offer', blank=True, related_name='cockpit_offers')
    created = models.DateTimeField(blank=True, default=datetime.now)
    emp_news = models.BooleanField(default=False)
    romande_news = models.BooleanField(default=False)
    automatic = models.BooleanField(default=False)
    month = models.BooleanField(default=False)
    weekdays = models.ManyToManyField('core.Weekday', blank=True)

    def __unicode__(self):
        return self.name


class NewsCategory(models.Model):
    name = models.CharField(blank=True, max_length=100)

    def __unicode__(self):
        return self.name


class News(models.Model):
    name = models.CharField(blank=True, max_length=100)
    category = models.ForeignKey(NewsCategory, blank=True, null=True)
    cockpit = models.ForeignKey(CockpitNews, blank=True, null=True)
    text = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


class CockpitMarket(models.Model):
    name = models.CharField(blank=True, max_length=100)
    # chart = models.ForeignKey(Chart, blank=True, null=True)
    category = models.ForeignKey(NewsCategory, blank=True, null=True)
    market_id = models.IntegerField(blank=True, null=True)
    currency = models.CharField(blank=True, max_length=100)
    description = models.CharField(blank=True, max_length=100)
    unit = models.CharField(blank=True, max_length=100)

    def __unicode__(self):
        return self.name


class Chart(models.Model):
    name = models.CharField(blank=True, max_length=100)
    cockpit = models.ForeignKey(CockpitNews, blank=True, null=True)
    markets = models.ManyToManyField(CockpitMarket, blank=True)
    tabel = models.BooleanField(default=False)
    chart = models.BooleanField(default=False)
    image = models.ImageField(blank=True, null=True, upload_to='cockpit/')

    def __unicode__(self):
        return self.name


class Cockpit(models.Model):
    name = models.CharField(blank=True, max_length=100)
    weekday = models.ForeignKey('core.Weekday', blank=True, null=True)

    def __unicode__(self):
        return self.name

    @property
    def weekdays(self):
        return Weekday.objects.all().values('name', 'day')


class CockpitOffer(models.Model):
    created = models.DateTimeField(blank=True, default=datetime.now)
    cockpit = models.ForeignKey(Cockpit, blank=True, null=True)
    offer = models.ForeignKey('offers.Offer', blank=True, null=True)
    highest = models.FloatField(blank=True, null=True)
    lowest = models.FloatField(blank=True, null=True)
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    weekday = models.ForeignKey('core.Weekday', blank=True, null=True)

    def __unicode__(self):
        return str(self.created)


class OfferHistory(models.Model):
    created = models.DateTimeField(blank=True, default=datetime.now)
    offer = models.ForeignKey('offers.Offer', blank=True, null=True)
    pfc = models.ForeignKey('pfc.PFC', blank=True, null=True)
    pfc_market = models.ForeignKey('pfc.PFCMarket', blank=True, null=True)
    accepted = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.created)
