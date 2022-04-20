from itertools import chain , groupby
from collections import defaultdict
from operator import itemgetter
from django.db import models
import numpy as np
import csv
import pytz
from pytz import country_timezones
from core.models import *
from pfc.models import *
from offers.models import *
from translations.models import *

from logic.report.budget import *
from logic.report.report import produce_budget_report
from logic.report.weekly import weekly_values
from logic.db.upload import upload_budget
from logic.db.weekly import uploadweekly


def get_oct_sunday(year, day_list=[6]):
    tmp_list = list()
    date_list = list()
    from_date = datetime(year=year, month=10, day=1)
    to_date = datetime(year=year, month=11, day=1)
    ## Creates a list of all the dates falling between the from_date and to_date range
    for x in xrange((to_date - from_date).days):
        tmp_list.append(from_date + timedelta(days=x))
    for date_record in tmp_list:
        if date_record.weekday() in day_list:
            date_list.append(date_record)

    return str(sorted(date_list)[-1])[5:10]


class Budget(models.Model):
    budget_id = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(default=datetime.now, blank=True)
    pfc = models.ForeignKey('pfc.PFC', null=True, blank=True, related_name='pfc_budget')
    pfc_market = models.ForeignKey('pfc.PFCMarket', null=True, blank=True, related_name='pfc_market_budget')
    cc = models.ForeignKey('companies.Meter', null=True, related_name='cc_budget')
    budget_report = models.FileField(null=True, blank=True)
    year = models.IntegerField(blank=True, null=True)
    site = models.ForeignKey('companies.Site', null=True, related_name='budget_site')
    unit = models.CharField(max_length=255, null=True, blank=True)
    offer = models.ForeignKey('offers.Offer', null=True, related_name='budget_offer')
    lissage = models.BooleanField(default=False)


    def __unicode__(self):
        return '{} : {}'.format(self.budget_id, self.year)

    class Meta:
        ordering = ('-pk',)

    def produce_report(self):
        cet = pytz.timezone('UTC')
        cett = pytz.timezone('CET')
        group_data = defaultdict(list)
        stream = StringIO.StringIO()
        writer = csv.writer(stream, delimiter='\t')
        # data_year = int(datetime.now().year)-1
        # print 'year == ', self.cc.site.year
        data_year = self.cc.site.year
        # print data_year
        # pfc_years = map(lambda x: data_year + x, range(5))
        # pfc_market_years = map(lambda x: data_year + x, range(5,7))
        transaction_years = map(lambda x: data_year + x, range(1,7))
        # print 'transaction_years == ', transaction_years

        if self.offer.pfc_date_first:
            fdate = make_naive(self.offer.pfc_date_first, pytz.timezone('CET'))
            if fdate.year == int(self.year):
                data_from = cet.localize(datetime(int(self.year), fdate.month, fdate.day, 0, 0), is_dst=None)
            else:
                data_from = cet.localize(datetime(int(self.year), 01, 01, 0, 0), is_dst=None)
        else:
            data_from = cet.localize(datetime(int(self.year), 01, 01, 0, 0), is_dst=None)

        if self.offer.pfc_date_last:
            ldate = make_naive(self.offer.pfc_date_last, pytz.timezone('CET'))
            if ldate.year == int(self.year):
                data_to = cet.localize(datetime(int(self.year), ldate.month, ldate.day, 23, 59), is_dst=None)
            else:
                data_to = cet.localize(datetime(int(self.year), 12, 31, 23, 59), is_dst=None)
        else:
            data_to = cet.localize(datetime(int(self.year), 12, 31, 23, 59), is_dst=None)

        # data_from = cet.localize(datetime(self.year, 01, 01, 0, 0), is_dst=None)
        # data_to = cet.localize(datetime(self.year, 12, 31, 23, 59), is_dst=None)


        if self.year in transaction_years:
            # print 'budget year = ', self.year
            cc_data = list(TranslationRecord.objects.filter(meter=self.cc,
                                                       interval_start__gte=data_from,
                                                       interval_start__lte=data_to
                                                       ).values('interval_start', 'value').order_by('interval_start'))
        else:
            cc_data=list(EnergyConsumptionRecord.objects.filter(meter=self.cc,
                                                        interval_start__gte=data_from,
                                                        interval_start__lte=data_to
                                                        ).values('interval_start', 'value').order_by('interval_start'))

        # pfc_data = PfcMarketConsumptionRecord.objects.filter(pfc_market = self.pfc_market, interval_start__year = self.year, unit = self.unit).values('interval_start', 'value')
        if self.pfc and not self.pfc_market:
            pfc_data = list(PfcConsumptionRecord.objects.filter(pfc = self.pfc,
                                                           interval_start__gte=data_from,
                                                           interval_start__lte=data_to,
                                                           unit = self.unit
                                                           ).values('interval_start', 'value').order_by('interval_start'))
        if self.pfc_market and not self.pfc:
            pfc_data = list(PfcMarketConsumptionRecord.objects.filter(pfc_market=self.pfc_market,
                                                           interval_start__gte=data_from,
                                                           interval_start__lte=data_to,
                                                           unit = self.unit
                                                          ).values('interval_start', 'value').order_by('interval_start'))

        # # for cc in cc_data:
        # #     print 'cc value = ', cc
        pfc_cet_data = []
        pfc_oct_data = []
        ccd_cet_data = []
        ccd_oct_data = []
        for pfc in pfc_data:
            if str(pfc['interval_start'])[5:16] == get_oct_sunday(pfc['interval_start'].year) + ' 02:00':
                pfc_oct_data.append({'interval_start': pfc['interval_start'], 'value': pfc['value']})
            else:
                pfc_cet_data.append({'interval_start': pfc['interval_start'], 'value': pfc['value']})
        
        for ccd in cc_data:
            if str(ccd['interval_start'])[5:16] == get_oct_sunday(ccd['interval_start'].year) + ' 02:00':
                # print '30 value ==', ccd['interval_start'], get_oct_sunday(ccd['interval_start'].year) + ' 02:00'
                ccd_oct_data.append({'interval_start': ccd['interval_start'], 'value': ccd['value']})
            else:
                ccd_cet_data.append({'interval_start': ccd['interval_start'], 'value': ccd['value']})
        
        # for index, pfc in enumerate(pfc_oct_data):
        #     group_data[str(pfc['interval_start'])[:16]].append([pfc['value'], ccd_oct_data[index]['value']])

        # print group_data
        all_data = ccd_cet_data + pfc_cet_data
        data = []
        ccc_data = []
        rec_list = []
        cc_med_data = []
        cc_sum = 0
        bg_sum = 0
        for cd in cc_data:
            data_cet = make_naive(cd['interval_start'], pytz.timezone('UTC'))
            # data_cet = cd['interval_start']
            month_dic = str(data_cet)[:7]
            cc_med_data.append({month_dic: cd['value']})
            interval_cc = pytz.utc.localize(datetime.strptime(str(cd['interval_start'])[:16], '%Y-%m-%d %H:%M'))
            interval_cc_start = interval_cc.astimezone(pytz.timezone('UTC'))
            ccc_data.append({'interval_start': interval_cc_start, 'value': cd['value']})
            cc_sum += cd['value']
        for index in range(len(all_data)):
            group_data[str(all_data[index]['interval_start'])[:16]].append(all_data[index]['value'])
        for key in group_data:
            # print(' group data prod key ====== ', key, group_data[key], len(group_data[key]))
            weekday = int(datetime.strptime(key[:10], '%Y-%m-%d').isoweekday())
            hour = int(str(key)[11:13])
            interval_data = pytz.utc.localize(datetime.strptime(key, '%Y-%m-%d %H:%M'))
            interval_start = interval_data.astimezone(pytz.timezone('UTC'))
            writer.writerow([datetime.now(), int(self.id), float(np.prod(group_data[key])), interval_start, timedelta(hours=1), 'ct/MWh'])
            data.append({'interval_start': interval_start, 'value': np.prod(group_data[key])})
            rec_list.append({key: np.prod(group_data[key])})
        
        # print pfc_oct_data, ccd_oct_data
        for index, pfc in enumerate(pfc_oct_data):
            weekday = int(pfc['interval_start'].isoweekday())
            hour = int(str(pfc['interval_start'])[11:13])
            interval_data = pytz.utc.localize(datetime.strptime(key, '%Y-%m-%d %H:%M'))
            interval_start = interval_data.astimezone(pytz.timezone('UTC'))
            # print([datetime.now(), int(self.id), float(pfc['value'] * ccd_oct_data[index]['value']), interval_start, timedelta(hours=1), 'ct/MWh'])
            writer.writerow([datetime.now(), int(self.id), float(pfc['value'] * ccd_oct_data[index]['value']), interval_start, timedelta(hours=1), 'ct/MWh'])
            data.append({'interval_start': interval_start, 'value': np.prod(pfc['value'] * ccd_oct_data[index]['value'])})
        # print 'rec list = ', rec_list
        upload_budget(stream)
        weekly_values(self, rec_list)
        produce_budget_report(self, data, ccc_data)


        # print 'cc sum = ', cc_sum
        # print 'bg sum = ', sum(item['value'] for item in data)
        # print 'med = ', sum(item['value'] for item in data) / cc_sum
        # WeightedAverageRecord.objects.create(year=self.year, value=(sum(item['value'] for item in data) / cc_sum), unit=self.unit, budget_id=self.id)


class BudgetRecord(models.Model):
    value = models.FloatField()
    unit = models.CharField(max_length=255)
    interval_start = models.DateTimeField()
    budget = models.ForeignKey(Budget, null=True, related_name='budget')
    interval = models.DurationField(null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-interval_start',)

    def __unicode__(self):
        return '{}: {} {}'.format(
            self.interval_start, self.value, self.unit)


class BudgetSeasonRecord(models.Model):
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='budget_season')
    year = models.IntegerField(blank=True, null=True)
    season = models.CharField(max_length=255, null=True, blank=True)
    schedule = models.ForeignKey('core.Shedule', null=True, related_name='season_schedule')
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}: {} from season {}'.format(self.schedule, self.value, self.season)


class BudgetWeeklyRecord(models.Model):
    value = models.FloatField()
    unit = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='budget_weekly')
    year = models.IntegerField(blank=True, null=True)
    hour = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}: {} from year {}'.format(self.hour, self.value, self.year)


# Buget med for all year
class BudgetMedRecord(models.Model):
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='budget_med')
    year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)


class BudgetMedWithRiscsRecord(models.Model):
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='budget_med_riscs')
    year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)


    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}: {} from year {}'.format(self.season, self.value, self.year)


# Buget med for each season of a shedule
class BudgetMedSeasonRecord(models.Model):
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    season = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='budget_season_med')
    schedule = models.ForeignKey('core.Shedule', null=True, related_name='budget_season_med_season_schedule')
    year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)


# Buget med for each season of a shedule
class BudgetMedSeasonMajorationRecord(models.Model):
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    season = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='budget_maj_season_med')
    schedule = models.ForeignKey('core.Shedule', null=True, related_name='budget_maj_season_med_season_schedule')
    year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)


class BudgetMedSeasonWithRiscsRecord(models.Model):
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    season = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='budget_season_med_riscs')
    schedule = models.ForeignKey('core.Shedule', null=True, related_name='budget_season_med_riscs_season_schedule')
    year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}: {} from year {}'.format(self.season, self.value, self.year)


class BudgetAveragePerYear(models.Model):
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='year_average_budget')
    year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}:from year {}'.format(self.value, self.year)


class BudgetAverageMajorationPerYear(models.Model):
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='year_maj_average_budget')
    year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}:from year {}'.format(self.value, self.year)


class BudgetAveragePerYearRiscs(models.Model):
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='year_risc_average_budget')
    year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}:from year {}'.format(self.value, self.year)


class BudgetAverageClean(models.Model):
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='year_clean_average_budget')
    year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}:from year {}'.format(self.value, self.year)


class BudgetAverageWithoutEfort(models.Model):
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='year_without_efort_average_budget')
    year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}:from year {}'.format(self.value, self.year)


class WeightedAverageRecord(models.Model):
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, null=True, related_name='average_budget')
    year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}:from year {}'.format(self.value, self.year)
