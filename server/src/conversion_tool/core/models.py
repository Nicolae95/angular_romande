from __future__ import division
from datetime import datetime, timedelta, time
import calendar
from collections import OrderedDict
from collections import defaultdict
from django.dispatch import receiver
from django.db.models.signals import post_save
from dateutil.rrule import rrule, MONTHLY
from operator import itemgetter
from django.db import models, connection
# from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Q, Func, Sum, Max, Count
from django.core.files.base import ContentFile
from model_utils.models import TimeStampedModel
import io
import csv
import os
import re
from geo.models import Location
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils.timezone import override as override_timezone
import pytz
from pytz import country_timezones
import StringIO
import xlsxwriter
from geo.models import Holiday
from django.db import transaction
# from django.db.models.expressions import DateTime
# Create your models here.
from itertools import groupby
from xlrd import open_workbook, xldate
from operator import itemgetter
import utils
from contextlib import closing
from django.db import connection
from logic.upload_data import *
from logic.db.upload import *
from companies.models import *
from core.models import *
from core.logic.peak import peak_data, med_month, months, weekly, headge

timezone_country = {}
for countrycode in country_timezones:
    timezones = country_timezones[countrycode]
    for timezone in timezones:
        timezone_country[timezone] = countrycode
        timezone_country[countrycode] = timezone


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

class BulkUpload(TimeStampedModel):

    def __unicode__(self):
        return 'Created at {}, id: {}'.format(str(self.created), str(self.id))


class EnergyConsumptionFile(TimeStampedModel):
    site = models.ForeignKey('companies.Site', null=True, blank=True)
    data_file = models.FileField()
    bulk_upload = models.ForeignKey(BulkUpload, null=True, blank=True)
    meters = models.ManyToManyField('companies.Meter', blank=True)
    multi = models.BooleanField(default=False)
    sum_file = models.BooleanField(default=False)

    def __unicode__(self):
        return self.data_file.name

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         super(EnergyConsumptionFile, self).save(*args, **kwargs)
    #         self.process_file(self.data_file.file)
    #     super(EnergyConsumptionFile, self).save(*args, **kwargs)

    # @transaction.atomic
    def process_file(self):
        cet = pytz.timezone('UTC')
        parse = False
        print self.data_file.file
        fileName, fileExtension = os.path.splitext(self.data_file.file.name)
        print fileName, fileExtension
        print 'multi in ', self.multi
        data_list = []
        weekly_list = []
        if self.multi == True :
            if fileExtension.lower() == '.xlsx' or fileExtension.lower() == '.xls':
                print (self, self.id, self.site, self.meters.all(), self.data_file.file)
                upload_cc_xls(self, self.id, self.site, self.meters.all(), self.data_file.file)
            elif fileExtension.lower() == '.csv':
                data_list, weekly_list = upload_cc_csv(self.id, self.site, self.data_file.file.name)
            else:
                return 'Error'
        elif self.multi == False:
            if fileExtension.lower() == '.xlsx' or fileExtension.lower() == '.xls':
                data_list, weekly_list = upload_cc_unic_xls(self, self.meters.all(), self.data_file.file)
            else:
                print 'Error'

    def sum_meters(self, msum):
        stream = StringIO.StringIO()
        writer = csv.writer(stream, delimiter='\t')
        cet = pytz.timezone('UTC')
        print 'sum meters', msum
        meters = Meter.objects.filter(site=self.site, meter_sum=False).values_list('id' , flat=True)
        data = EnergyConsumptionRecord.objects.filter(meter_id__in=meters).values('interval_start').annotate(Sum('value'))
        # print data
        for dt in data:
            if str(dt['interval_start'])[5:16] != get_oct_sunday(dt['interval_start'].year, day_list=[6]) + ' 02:00':
                writer.writerow([datetime.now(), datetime.now(), int(msum.id), dt['value__sum'], dt['interval_start'], timedelta(hours=1), 'kWh'])
        
        oct_data = []
        hour = datetime(2017, 3, 13)
        for meter in meters:
            hour_data=EnergyConsumptionRecord.objects.filter(meter = meter).values('interval_start', 'value')
            for hd in hour_data:
                if str(hd['interval_start'])[5:16] == get_oct_sunday(hd['interval_start'].year, day_list=[6]) + ' 02:00':
                    print hd['interval_start'], hd['value']
                    oct_data.append(hd['value'])
                    hour = hd['interval_start']
        first = 0
        last = 0
        for index, oc in enumerate(oct_data):
            if index % 2 == 0:
                first += oc
            else:
                last += oc
        print 'hour === ', hour
        writer.writerow([datetime.now(), datetime.now(), int(msum.id), first, hour, timedelta(hours=1), 'kWh'])
        writer.writerow([datetime.now(), datetime.now(), int(msum.id), last, hour, timedelta(hours=1), 'kWh'])
        upload_null(stream)

class EnergyConsumptionRecord(TimeStampedModel):
    from_file = models.ForeignKey(EnergyConsumptionFile, null=True, blank=True)
    meter = models.ForeignKey('companies.Meter')
    value = models.FloatField()
    unit = models.CharField(max_length=255)
    interval_start = models.DateTimeField()
    interval = models.DurationField()

    class Meta:
        ordering = ('-interval_start',)

    def __unicode__(self):
        return '{}: {} {} from file {}'.format(
            self.interval_start, self.value, self.unit, self.from_file_id)

    def get_weekday_name(self):
        return calendar.day_name[self.interval_start.weekday()]

    def get_weekday_code(self):
        return self.interval_start.toordinal() % 7 + 1


class MonthRecord(models.Model):
    value = models.FloatField()
    unit = models.CharField(max_length=255)
    meter = models.ForeignKey('companies.Meter', null=True, related_name='meter_month')
    schedule = models.ForeignKey('core.Shedule', null=True, related_name='meter_month_schedule')
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}: {} from year {}'.format(self.month, self.value, self.year)


class WeeklyRecord(models.Model):
    value = models.FloatField()
    unit = models.CharField(max_length=255)
    meter = models.ForeignKey('companies.Meter', null=True, related_name='meter_weekly')
    year = models.IntegerField(blank=True, null=True)
    hour = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}: {} from year {}'.format(self.hour, self.value, self.year)


class HeadgeRecord(models.Model):
    value = models.FloatField()
    unit = models.CharField(max_length=255)
    meter = models.ForeignKey('companies.Meter', null=True, related_name='meter_headge')
    schedule = models.ForeignKey('core.Shedule', null=True, related_name='meter_headge_schedule')
    year = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}: {} from year {}'.format(self.schedule.title, self.value, self.year)


class DayPattern(TimeStampedModel):
    WEEKDAY_CHOICES = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
        ('public_holiday', 'Public Holiday'),
    )
    weekday = models.CharField(max_length=255, choices=WEEKDAY_CHOICES)
    hours = models.ManyToManyField('Hour', blank=True)

    def __unicode__(self):
        return '{}: {}'.format(
            self.weekday,
            ','.join([str(hour.value) for hour in self.hours.all()])
        )


class Hour(models.Model):
    value = models.SmallIntegerField(unique=True)

    def __unicode__(self):
        return str(self.value)

    class Meta:
        ordering = ('-value',)

class Months(models.Model):
    name = models.CharField(max_length=255)
    month = models.SmallIntegerField(unique=True)

    def __unicode__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Months"

class Weekday(models.Model):
    name = models.CharField(max_length=255)
    day = models.SmallIntegerField(unique=True)

    def __unicode__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Weekdays"

class EnergyConsumptionPeriod(TimeStampedModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    weekdays = models.ManyToManyField(DayPattern)

    def __unicode__(self):
        return self.title


def unique_chain(*iterables):
    known_ids = set()
    for it in iterables:
        for element in it:
            if element.id not in known_ids:
                known_ids.add(element.id)
                yield element


class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()



class Year(Func):
    function = 'EXTRACT'
    template = '%(function)s(YEAR from %(expressions)s)'
    output_field = models.IntegerField()


class Shedule(TimeStampedModel):
    title = models.CharField(max_length=255)
    hours = models.ManyToManyField('Hour')
    months = models.ManyToManyField('Months')
    weekdays = models.ManyToManyField('Weekday', related_name='weekdays')
    country = models.ForeignKey(Location, on_delete=models.CASCADE)
    holiday = models.BooleanField(default=False)
    off_holiday = models.BooleanField(default=False)
    all_holidays = models.BooleanField(default=False)
    weekend = models.BooleanField(default=False)
    weekend_days = models.ManyToManyField('Weekday', blank=True, related_name='weekend_days')

    def __unicode__(self):
        return self.title


class SeasonRecord(models.Model):
    value = models.FloatField()
    unit = models.CharField(max_length=255)
    meter = models.ForeignKey('companies.Meter', null=True, related_name='meter_season')
    schedule = models.ForeignKey(Shedule, null=True, related_name='meter_season_schedule')
    year = models.IntegerField(blank=True, null=True)
    season = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}: {} from season {}'.format(self.schedule.title, self.value, self.season)


# class TranslationRecords(TimeStampedModel):
#     title = models.CharField(max_length=255)
#     translation_meter = models.ForeignKey('companies.Meter', related_name='translation_meter')
#     # year = models.CharField(max_length=255, null=True, blank=True)
#     # translated_year = models.CharField(max_length=255, null=True, blank=True)
#
#     def __unicode__(self):
#         return self.title
#
#     def save(self, *args, **kwargs):
#         super(TranslationRecords, self).save(*args, **kwargs)
#         self.process_data()
#
#     def process_data(self):
#         cet = pytz.timezone('utc')
#         frecord = EnergyConsumptionRecord.objects.filter(meter=self.translation_meter).order_by('interval_start')[0]
#         data_year = int(frecord.interval_start.year)
#         td = frecord.interval
#         cc_from = cet.localize(datetime(data_year, 01, 01, 0, 0), is_dst=None)
#         cc_to = cet.localize(datetime(data_year, 12, 31, 23, 59), is_dst=None)
#         cet_cc_from = make_aware(cc_from.replace(tzinfo=None), cet, is_dst=None)
#         cet_cc_to = make_aware(cc_to.replace(tzinfo=None), cet, is_dst=None)
#
#         all_data = EnergyConsumptionRecord.objects.filter(
#             meter=self.translation_meter,
#             interval_start__gte=cet_cc_from,
#             interval_start__lte=cet_cc_to
#         ).order_by('interval_start')
#
#         # datas = all_data.values('interval_start', 'value').order_by('interval_start')
#         # print datas.filter(interval_start__week_day=2)
#
#         holidays = Holiday.objects.filter(
#             country=self.translation_meter.site.location.country,
#             date__year=data_year,
#         ).values_list('date', flat=True)
#
#         holiday_list = []
#
#         for v in holidays:
#             holiday_list.append(v.isoformat())
#         # print 'holiday data =', holiday_list
#
#         holidays_meter = []     # holidays by hour (of the data that will be translated)
#         data_by_day = defaultdict(list)
#         for dt in all_data:
#             w_cet = make_naive(dt.interval_start, cet)
#             weekdend = str(w_cet)[5:16]
#             if str(w_cet)[:10] in holiday_list:
#                 holidays_meter.append({'hour':weekdend, 'value': dt.value})
#                 # data_by_day[str(dt.interval_start.weekday())].append({'hour':weekdend, 'value':dt.value})
#             else:
#                 data_by_day[str(dt.interval_start.weekday())].append({'hour':weekdend, 'value':dt.value})
#
#         d_file = all_data.values('from_file')[0]
#         data_file = EnergyConsumptionFile.objects.get(id=d_file['from_file'])
#         # print data_by_day
#
#         translation_years = map(lambda x: data_year + x, range(1,7))
#         # translation_years = [2017, 2018, 2019, 2020]
#
#         stream = StringIO.StringIO()
#         writer = csv.writer(stream, delimiter='\t')
#         # n_records = 0
#         for translated_year in translation_years:
#             print 'trnaslated year = ', translated_year
#             tc_from = cet.localize(datetime(int(translated_year), 01, 01, 0, 0), is_dst=None)
#             tc_to = cet.localize(datetime(int(translated_year), 12, 31, 23, 59), is_dst=None)
#             translated_holidays = Holiday.objects.filter(
#                 country=self.translation_meter.site.location.country,
#                 date__year=translated_year,
#             ).values_list('date', flat=True)
#
#             translated_holiday_list = []
#             for v in translated_holidays:
#                 translated_holiday_list.append(v.isoformat())
#
#             print 'holiday list = ', translated_holiday_list
#             print 'data ', tc_from, tc_to , td
#             last = tc_to
#             holiday_days = []       # weekend days by hour (of the translated year)
#             next_day = tc_from
#             data_translated = defaultdict(list)
#             print next_day
#
#             while True:
#                 if next_day > tc_to:
#                     break
#                     next_day = make_naive(next_day, cet)
#
#                 if str(next_day)[:10] in translated_holiday_list:
#                     holiday_days.append(str(next_day)[5:16])
#                 else:
#                     data_translated[str(next_day.weekday())].append(str(next_day)[5:16])
#                 next_day += td
#                 # print str(next_day)
#
#
#             #
#             # # Holiday translation
#             #
#
#             hol_min = min([len(holiday_days),len(holidays_meter)])
#             hol_rows = []
#             for k in range(hol_min):
#                 # print 'Holiday day ===', holidays_meter[k], holiday_days[k]
#                 print 'holiday = ', str(translated_year), holiday_days[k][:2], holiday_days[k][3:5], holiday_days[k][6:8], holiday_days[k][9:11], holiday_days[k]
#                 hol_data = pytz.utc.localize(datetime(int(translated_year), int(holiday_days[k][:2]), int(holiday_days[k][3:5]), int(holiday_days[k][6:8]), int(holiday_days[k][9:11])))
#                 interval_start = hol_data.astimezone(pytz.timezone('UTC'))
#                 writer.writerow([datetime.now(), datetime.now(), int(data_file.id), int(self.translation_meter.id), holidays_meter[k]['value'], interval_start, td, 'kWh'])
#
#                 # record = EnergyConsumptionRecord(
#                 #     from_file=data_file,
#                 #     meter=self.translation_meter,
#                 #     value=holidays_meter[k]['value'],
#                 #     interval_start=interval_start,
#                 #     interval=td,
#                 #     unit='kWh'
#                 # )
#                 # print 'Holiday record == ', record
#                 # hol_rows.append(record)
#             # EnergyConsumptionRecord.objects.bulk_create(hol_rows)
#
#
#             #
#             # # All remained days translation
#             #
#
#             data_rows = []
#             for key in data_by_day.keys():
#                 min_val = min(len(data_by_day[key]), len(data_translated[key]))
#                 if min_val == len(data_translated[key]):
#                     for index in range(min_val):
#                         # data_rows.append({self.translated_year + ' ' + data_translated[key][index]: data_by_day[key][index]['value']})
#                         print 'key min_val == len(data_translated[key]) == ', key, str(translated_year) + ' ' + data_translated[key][index], data_by_day[key][index]['value'], (len(data_translated[key]) - len(data_by_day[key]))
#                         hol_data = pytz.utc.localize(datetime(int(translated_year), int(data_translated[key][index][:2]), int(data_translated[key][index][3:5]), int(data_translated[key][index][6:8]), int(data_translated[key][index][9:11])))
#                         interval_start = hol_data.astimezone(pytz.timezone('UTC'))
#                         writer.writerow([datetime.now(), datetime.now(), int(data_file.id), int(self.translation_meter.id), data_by_day[key][index]['value'], interval_start, td, 'kWh'])
#
#                         # record = EnergyConsumptionRecord(
#                         #     from_file=data_file,
#                         #     meter=self.translation_meter,
#                         #     value=data_by_day[key][index]['value'],
#                         #     interval_start=interval_start,
#                         #     interval=timedelta(minutes=15),
#                         #     unit='kWh'
#                         # )
#                         # data_rows.append(record)
#
#                 elif min_val == len(data_by_day[key]):
#                     # print data_translated[key][0] , data_by_day[key][0]['hour'], len(data_translated[key]) , len(data_by_day[key]), len(data_translated[key]) - len(data_by_day[key])
#                     data_by_day[key] = data_by_day[key] + data_by_day[key][-(len(data_translated[key]) - len(data_by_day[key])):]
#                     for index in range(len(data_by_day[key])):
#                         print 'key min_val == len(data_by_day[key]) == ', key, str(translated_year) + ' ' + data_translated[key][index], data_by_day[key][index]['value'], (len(data_translated[key]) - len(data_by_day[key]))
#                         hol_data = pytz.utc.localize(datetime(int(translated_year), int(data_translated[key][index][:2]), int(data_translated[key][index][3:5]), int(data_translated[key][index][6:8]), int(data_translated[key][index][9:11])))
#                         interval_start = hol_data.astimezone(pytz.timezone('UTC'))
#                         writer.writerow([datetime.now(), datetime.now(), int(data_file.id), int(self.translation_meter.id), data_by_day[key][index]['value'], interval_start, td, 'kWh'])
#
#                         # record = EnergyConsumptionRecord(
#                         #     from_file=data_file,
#                         #     meter=self.translation_meter,
#                         #     value=data_by_day[key][index]['value'],
#                         #     interval_start=interval_start,
#                         #     interval=timedelta(minutes=15),
#                         #     unit='kWh'
#                         # )
#                         # data_rows.append(record)
#
#             # EnergyConsumptionRecord.objects.bulk_create(data_rows)
#
#         stream.seek(0)
#         with closing(connection.cursor()) as cursor:
#             cursor.copy_from(
#                 file=stream,
#                 table='core_energyconsumptionrecord',
#                 sep='\t',
#                 columns=('created', 'modified', 'from_file_id', 'meter_id', 'value', 'interval_start', 'interval', 'unit'),
#             )
#
# class SumDiffReport(TimeStampedModel):
#     title = models.CharField(max_length=255)
#     meters = models.ManyToManyField('companies.Meter', blank=True, related_name='meters')
#     datetime_from = models.DateTimeField()
#     datetime_to = models.DateTimeField()
#     shedules = models.ManyToManyField(Shedule, related_name='sum_shedules')
#     report_file = models.FileField(null=True, blank=True)
#     meter_name = models.CharField(max_length=255, blank=True)
#     unit = models.CharField(max_length=255, blank=True)
#     diff_bool = models.BooleanField(default=False)
#     diff_cc = models.IntegerField(default=0, null=True, blank=True)
#
#     def replace(self):
#         if self.unit != None:
#             unit = self.unit
#             return u'%s' % (unit.replace('/', '_'))
#
#     unit_sum = property(replace)
#
#     def replace_total(self):
#         return u'%s' % (self.meters.meter_id[:10] + '...')
#
#     meter_new = property(replace_total)
#
#     def __unicode__(self):
#         return self.title
#
#     # @override_timezone(pytz.timezone('CET'))
#     def produce_sum_diff_report(self):
#         # countryz = self.shedules.all()[0].country.country
#         # cet = pytz.timezone(timezone_country[str(countryz)])
#         cet = pytz.timezone('UTC')
#         print cet
#         print 'producing report'
#         _weekdays = [
#             'sunday', 'monday', 'tuesday',
#             'wednesday', 'thursday', 'friday', 'saturday'
#         ]
#         print 'DATA FROM = ', self.datetime_from, type(self.datetime_from)
#
#         cet_dt_from = make_aware(
#             self.datetime_from.replace(tzinfo=None), cet, is_dst=None)
#
#         cet_dt_to = make_aware(
#             self.datetime_to.replace(tzinfo=None), cet, is_dst=None)
#         print cet_dt_from, cet_dt_to
#
#         holidays = Holiday.objects.filter(
#             country=self.meters.all()[0].site.location.country,
#             region=self.meters.all()[0].site.location.region,
#             date__gte=cet_dt_from.date(),
#             date__lte=cet_dt_to.date()
#         )
#
#         first_holiday_year = str(cet_dt_from)[:4]
#         sec_holiday_year = str(cet_dt_to)[:4]
#
#         adata = EnergyConsumptionRecord.objects.filter(
#             meter=self.meters.all()[0],
#         ).order_by('interval_start')
#
#         d_file = adata.values('from_file')[0]
#         data_file = EnergyConsumptionFile.objects.get(id=d_file['from_file'])
#         data_unit = adata.values('unit')[0]
#         self.unit = data_unit['unit']
#
#         meters_list = defaultdict(list)
#         meters_res = []
#         meters_all = []
#
#         m_name = 'Total_'
#         for meter in self.meters.all():
#             m_name += meter.meter_id + '_'
#
#             all_data = EnergyConsumptionRecord.objects.filter(
#                 meter=meter,
#                 interval_start__gte=cet_dt_from,
#                 interval_start__lte=cet_dt_to
#             ).order_by('interval_start')
#
#             peak_data_rec_list = defaultdict(list)
#             peak_rec_data_res = []
#
#             datas = all_data.values('interval_start', 'value')
#
#             rec_list = []
#
#             for data in datas:
#                 data_cc_cet = make_naive(data['interval_start'], cet)
#                 rec_hour = str(data_cc_cet)[:13]
#                 rec_list.append({rec_hour: data['value']})
#
#             #
#             # Sum per hour Peak values
#             #
#             for d in rec_list: # you can list as many input dicts as you want here
#                 for key, value in d.iteritems():
#                     peak_data_rec_list[key].append(value)
#
#             for key in peak_data_rec_list.keys():
#                 peak_rec_data_res.append({'value' : sum(item for item in peak_data_rec_list[key]), 'interval_start' : key+':00'})
#
#             peak_rec_data_res = sorted(peak_rec_data_res, key=itemgetter('interval_start'))
#
#             for data_meter in peak_rec_data_res: # you can list as many input dicts as you want here
#                 meters_all.append({data_meter['interval_start']: data_meter['value']})
#             # meters_all.append(peak_rec_data_res)
#
#         #
#         # Diff from sum value
#         #
#         print self.diff_bool
#         if self.diff_bool == True:
#             diff_meters = []
#             cc = Meter.objects.get(id = self.diff_cc)
#             diff_data = EnergyConsumptionRecord.objects.filter(
#                 meter=cc,
#                 interval_start__gte=cet_dt_from,
#                 interval_start__lte=cet_dt_to
#             ).order_by('interval_start')
#
#             peak_data_diff_list = defaultdict(list)
#             peak_diff_data_res = []
#
#             diff_datas = diff_data.values('interval_start', 'value')
#
#             diff_list = []
#
#             for data in diff_datas:
#                 data_cc_diff = make_naive(data['interval_start'], cet)
#                 rec_hour = str(data_cc_diff)[:13]
#                 diff_list.append({rec_hour: data['value']})
#             #
#             # Sum per hour of the diff
#             #
#             for d in diff_list: # you can list as many input dicts as you want here
#                 for key, value in d.iteritems():
#                     peak_data_diff_list[key].append(value)
#
#             for key in peak_data_diff_list.keys():
#                 peak_diff_data_res.append({'value' : sum(item for item in peak_data_diff_list[key]), 'interval_start' : key+':00'})
#
#             peak_diff_data_res = sorted(peak_diff_data_res, key=itemgetter('interval_start'))
#
#             for data_meter in peak_diff_data_res: # you can list as many input dicts as you want here
#                 diff_meters.append({data_meter['interval_start']: data_meter['value']})
#                 # print 'diff meters = ', data_meter['interval_start'], data_meter['value']
#
#
#             diff_result = []
#             for index in range(len(diff_meters)):
#                 for key, value in diff_meters[index].iteritems():
#                     diff_result.append({key: value - meters_all[index][key]})
#                     # print 'diff == ', key, value, meters_all[index][key], value - meters_all[index][key]
#
#             for d in diff_result: # you can list as many input dicts as you want here
#                 for key, value in d.iteritems():
#                     meters_list[key].append(value)
#
#             for key in meters_list.keys():
#                 meters_res.append({'value' : sum(item for item in meters_list[key]), 'interval_start' : key})
#             meters_res = sorted(meters_res, key=itemgetter('interval_start'))
#
#
#
#         if self.diff_bool == False:
#             for d in meters_all: # you can list as many input dicts as you want here
#                 for key, value in d.iteritems():
#                     meters_list[key].append(value)
#
#             for key in meters_list.keys():
#                 meters_res.append({'value' : sum(item for item in meters_list[key]), 'interval_start' : key})
#             meters_res = sorted(meters_res, key=itemgetter('interval_start'))
#
#         # print meters_res
#         # print 'new meter == ', m_name
#
#         self.meter_name = m_name
#
#         meter, created = Meter.objects.get_or_create(
#             meter_id = self.meter_name, site=self.meters.all()[0].site)
#
#         rows = []
#         datemt = pytz.utc.localize(datetime.strptime(meters_res[10]['interval_start'], '%Y-%m-%d %H:%M'))
#
#         if EnergyConsumptionRecord.objects.filter(interval_start=datemt, value=float(meters_res[10]['value'])).exists() == False:
#             for met in meters_res:
#                 datem = pytz.utc.localize(datetime.strptime(met['interval_start'], '%Y-%m-%d %H:%M'))
#                 # print met
#                 record = EnergyConsumptionRecord(
#                     from_file=data_file,
#                     meter=meter,
#                     value=float(met['value']),
#                     interval_start=datem,
#                     interval=timedelta(hours=1),
#                     unit=data_unit['unit']
#                 )
#                 rows.append(record)
#             EnergyConsumptionRecord.objects.bulk_create(rows)
#
#         months_all = [str(dt)[:7] for dt in rrule(MONTHLY, dtstart=cet_dt_from, until=cet_dt_to)]
#         print months_all
#
#         shed_len_max = []
#         for sh in self.shedules.all() :
#             shed_len_max.append(len(sh.months.all().values_list('month', flat=True)))
#
#         output = StringIO.StringIO()
#         workbook = xlsxwriter.Workbook(output, {'in_memory': True})
#         worksheet = workbook.add_worksheet()
#
#         date_format = workbook.add_format({'num_format': 'm/d/yy'})
#         time_format = workbook.add_format({'num_format': 'hh:mm'})
#         scurt_format = workbook.add_format({'num_format': '0.00'})
#
#         text_format = workbook.add_format()
#         text_format.set_text_wrap()
#
#         # Widen column A for extra visibility.
#         worksheet.set_column('A:A', 10)
#         worksheet.set_column('B:B', 15)
#         worksheet.set_column('C:C', 15)
#         worksheet.set_column('P:P', 13)
#         chart = workbook.add_chart({'type': 'line'})
#         # Write some test data.
#         bold_format = workbook.add_format({'bold': True})
#
#         worksheet.write(0, 0, 'Report', bold_format)
#         worksheet.write(0, 1, self.title)
#
#
#         import calendar
#
#         sheet_col = {}
#         for i, month in enumerate(months_all):
#             worksheet.write(2, 3 + i, month)
#             sheet_col[month] = 3 + i
#             # worksheet.write(2, 3 + p, calendar.month_name[int(month)])
#
#         total = []
#         total_max = []
#         weekly = []
#
#         for index, shedule in enumerate(self.shedules.all()):
#             hourss = shedule.hours.all().values_list('value', flat=True)
#             months = shedule.months.all().values_list('month', flat=True)
#             weekdays = shedule.weekdays.all().values_list('day', flat=True)
#             weekend_days = shedule.weekend_days.all().values_list('day', flat=True)
#             hol = shedule.country.holidays.all().values_list('date', flat=True)
#             holiday_list = []
#
#             for v in hol:
#                 h = str(v)[:4]
#                 if h == first_holiday_year:
#                     holiday_list.append(v.isoformat())
#                 elif (first_holiday_year != sec_holiday_year and h == sec_holiday_year):
#                     holiday_list.append(v.isoformat())
#
#             rec_list = []
#             peak_list = []
#             for data in meters_res:
#                 data_cet = data['interval_start']
#                 weekday = int(datetime.strptime(str(data_cet)[:10], '%Y-%m-%d').isoweekday())
#                 hours = int(str(data_cet)[11:13])
#                 hour = time(int(str(data_cet)[11:13]), int(str(data_cet)[14:16]))
#                 day = str(data_cet)[:10]
#                 month_dic = str(data_cet)[:7]
#                 month = int(str(data_cet)[5:7])
#                 rec_hour = str(data_cet)[:13]
#                 rec_list.append({rec_hour: data['value']})
#
#                 if ((hours in hourss) and (month in months) and (weekday in weekdays) and ((day not in holiday_list) == True)):
#                     peak_list.append({month_dic: data['value']})
#
#                 if ((day in holiday_list) == True) and (shedule.holiday == True):
#                     if ((hours in hourss) and (month in months) and (weekday in weekdays)):
#                         peak_list.append({month_dic: data['value']})
#                         # print 'Holiday with first checkbox = ', shedule.title, data_cet, month_dic, data['value']
#
#                 if ((weekday in weekend_days) and (month in months) and ((day in holiday_list) == True) and (shedule.weekend == True) and (shedule.holiday == True)):
#                     peak_list.append({month_dic: data['value']})
#                     # print 'Holiday as normal coincide cu weekend = ', shedule.title, data_cet, data['value']
#
#                 if (((day in holiday_list) == True) and (month in months) and (shedule.all_holidays == True)):
#                     peak_list.append({month_dic: data['value']})
#                     # print shedule.title, shedule.all_holidays, 'All holidays ========== ', data['interval_start'], data['value']
#
#                 if ((weekday in weekend_days) and (month in months) and ((day not in holiday_list) == True) and (shedule.weekend == True)):
#                     peak_list.append({month_dic: data['value']})
#                     # print shedule.title, shedule.weekend, 'All weekend data ========== ', data['interval_start'], data['value']
#
#
#             peak_data_list = defaultdict(list)
#             peak_data_rec_list = defaultdict(list)
#             peak_data_res = []
#             peak_rec_data_res = []
#             peak_data_med_res = defaultdict(list)
#             peak_data_res_shedule = []
#
#             #
#             # Sum per month Peak values
#             #
#
#             for d in peak_list: # you can list as many input dicts as you want here
#                 for key, value in d.iteritems():
#                     peak_data_list[key].append(value)
#
#
#             for key in peak_data_list.keys():
#                 # peak_data_res.append({'month':key, 'max' : max(item for item in peak_data_list[key]), 'value' : sum(item for item in peak_data_list[key])/ len(peak_data_list[key])-1 })
#                 peak_data_res.append({'month':key, 'max' : max(item for item in peak_data_list[key]), 'lenght': len(peak_data_list[key])-1, 'value' : sum(item for item in peak_data_list[key])})
#
#             peak_data_res = sorted(peak_data_res, key=itemgetter('month'))
#
#
#             #
#             # Sum per hour Peak values
#             #
#
#             for d in rec_list: # you can list as many input dicts as you want here
#                 for key, value in d.iteritems():
#                     peak_data_rec_list[key].append(value)
#
#             for key in peak_data_rec_list.keys():
#                 weekday = int(datetime.strptime(key[:10], '%Y-%m-%d').isoweekday())
#                 hour = int(str(key)[11:13])
#                 peak_rec_data_res.append({'hour':key+':00', 'value' : sum(item for item in peak_data_rec_list[key])})
#                 # weekly.append({'hour':key+':00', 'weekhour': (weekday-1)*24+hour, 'value' : sum(item for item in peak_data_rec_list[key])})
#                 weekly.append({(weekday-1)*24+hour: sum(item for item in peak_data_rec_list[key])})
#                 # print 'hour = ', key, 'weekhour', (weekday-1)*24+hour, 'value' , sum(item for item in peak_data_rec_list[key])
#
#
#             peak_rec_data_res = sorted(peak_rec_data_res, key=itemgetter('hour'))
#
#             # print 'peak_rec_data_res ===== ', peak_rec_data_res
#
#             #
#             # Media Peak values
#             #
#
#             for key in peak_data_list.keys():
#                 peak_data_res_shedule += peak_data_list[key]
#                 month_med = datetime.strptime(key,'%Y-%m').month
#                 if month_med in [4,5,6,7,8,9]:
#                     peak_data_med_res['summer'] += peak_data_list[key]
#                 else :
#                     peak_data_med_res['winter'] += peak_data_list[key]
#
#             print index, len(self.shedules.all())
#             # print shedule.title, ' result dictionary == ', peak_data_res
#
#             total_peak = 0
#             max_list = []
#
#             if meters_all:
#                 worksheet.write(3, 2, 'Max', bold_format)
#                 worksheet.write(4+index, 2, shedule.title, bold_format)
#                 worksheet.write(9 + len(self.shedules.all()) + index, 8, shedule.title, bold_format)
#                 worksheet.write(9 + len(self.shedules.all()) + index, 9, sum(item for item in peak_data_med_res['summer']))
#                 worksheet.write(9 + len(self.shedules.all()) + index, 10, sum(item for item in peak_data_med_res['winter']))
#
#
#                 for p, value in enumerate(peak_data_res):
#                     total_peak += value['value']
#                     worksheet.write(4+index, sheet_col[value['month']] , value['value'])
#                     total.append({value['month']: value['value']})
#                     total_max.append({value['month']: value['max']})
#
#                 worksheet.write(2, len(months_all)-1 + 4, 'Total', bold_format)
#                 worksheet.write(4 + index, len(months_all)-1 + 4, total_peak, bold_format)
#
#                 # worksheet.write(4 + index, len(months_all)-1 + 4, sum(item for item in peak_data_res_shedule) , scurt_format)
#
#         worksheet.write(4 + len(self.shedules.all()), 2, 'Total(MWh)', bold_format)
#
#         #
#         # Media data by weekly hour
#         #
#         # print weekly
#
#         weekly_list = defaultdict(list)
#         weekly_res = []
#         for d in weekly: # you can list as many input dicts as you want here
#             for key, value in d.iteritems():
#                 weekly_list[key].append(value)
#
#         for key in weekly_list.keys():
#             weekly_res.append({'hour':key, 'value' : sum(item for item in weekly_list[key])/ len(weekly_list[key])})
#
#         weekly_res = sorted(weekly_res, key=itemgetter('hour'))
#         # print 'data per weekely hour ==== ', weekly_res
#
#
#         #
#         # Total for each month
#         #
#
#         total_data_list = defaultdict(list)
#         total_data_res = []
#         for d in total: # you can list as many input dicts as you want here
#             for key, value in d.iteritems():
#                 total_data_list[key].append(value)
#
#         for key in total_data_list.keys():
#             total_data_res.append({'month':key, 'total' : sum(item for item in total_data_list[key])})
#
#         total_data_res = sorted(total_data_res, key=itemgetter('month'))
#         # print total_data_res
#
#         total_months = 0
#         for p, t in enumerate(total_data_res):
#             total_months+=t['total']
#             worksheet.write(4 + len(self.shedules.all()), sheet_col[t['month']], t['total'], bold_format)
#
#         #
#         # Max for each month
#         #
#
#         total_max_data_list = defaultdict(list)
#         total_max_data_res = []
#
#         for d in total_max: # you can list as many input dicts as you want here
#             for key, value in d.iteritems():
#                 total_max_data_list[key].append(value)
#
#         for key in total_max_data_list.keys():
#             total_max_data_res.append({'month':key, 'max' : max(item for item in total_max_data_list[key])})
#
#         total_max_data_res = sorted(total_max_data_res, key=itemgetter('month'))
#         # print total_max_data_res
#         for p, m in enumerate(total_max_data_res):
#             worksheet.write(3, sheet_col[m['month']], m['max'])
#
#         worksheet.write(3, len(months_all)-1 + 4, max(total_max_data_res, key=lambda x:x['max'])['max'], bold_format)
#         worksheet.write(4 + len(self.shedules.all()), len(months_all)-1 + 4, total_months, bold_format)
#
#         worksheet.write(len(self.shedules.all()) + 8, 1, 'Date', bold_format)
#         worksheet.write(len(self.shedules.all()) + 8, 2, 'Time', bold_format)
#         worksheet.write(len(self.shedules.all()) + 8, 3, data_unit['unit'], bold_format)
#
#         worksheet.write(len(self.shedules.all()) + 8, 14, 'Weekly day', bold_format)
#         worksheet.write(len(self.shedules.all()) + 8, 15, 'Average value', bold_format)
#
#         # print 'peak days === ', [d['hour'][:10] for d in peak_rec_data_res]
#         # print 'peak hours === ', [d['hour'][11:13] for d in peak_rec_data_res]
#         # print 'peak values === ', [d['value'] for d in peak_rec_data_res]
#
#         worksheet.write_column('D'+ str(len(self.shedules.all()) + 10), [d['value'] for d in peak_rec_data_res])
#         worksheet.write_column('B'+ str(len(self.shedules.all()) + 10), [d['hour'][:10] for d in peak_rec_data_res])
#         worksheet.write_column('C'+ str(len(self.shedules.all()) + 10), [d['hour'][11:16] for d in peak_rec_data_res])
#
#
#         worksheet.write_column('O'+ str(len(self.shedules.all()) + 10), [d['hour'] for d in weekly_res])
#         worksheet.write_column('P'+ str(len(self.shedules.all()) + 10), [d['value'] for d in weekly_res])
#         #
#         # Average on summer and winter
#         #
#
#         worksheet.write(len(self.shedules.all()) + 8, 9, 'Summer', bold_format)
#         worksheet.write(len(self.shedules.all()) + 8, 10, 'Winter', bold_format)
#
#
#         workbook.close()
#
#         data_name = self.datetime_from
#         data_name_to = self.datetime_to
#
#         data = ContentFile(output.getvalue())
#         self.report_file.save(
#             name='{}-{}-{}_{}_{}.xlsx'.format(self.meters.all()[0].site.name, 'from', self.meters.all()[0].site.company, data_name.strftime("%b%d-%Y"), data_name_to.strftime("%b%d-%Y")),
#             content=data,
#             save=False
#         )
#         self.save()
#
#
# class BudgetReport(TimeStampedModel):
#     title = models.CharField(max_length=255)
#     budget = models.ForeignKey('companies.Meter', null=True, related_name='budget')
#     time_peak = models.TimeField(blank=True, null=True)
#     time_peakoff = models.TimeField(blank=True, null=True)
#     datetime_from = models.DateTimeField()
#     datetime_to = models.DateTimeField()
#     shedules = models.ManyToManyField(Shedule, related_name='budget_shedules')
#     budget_file = models.FileField(null=True, blank=True)
#     pfc = models.IntegerField(null=True, blank=True)
#     unit = models.CharField(max_length=255, blank=True)
#     self_unit = models.CharField(max_length=255, blank=True)
#
#     def replace_budg(self):
#         if self.unit != None:
#             unit = self.unit
#             return u'%s' % (unit.replace('/', '_'))
#
#     unit_bud = property(replace_budg)
#
#     def replace_pfc(self):
#         if self.unit != None:
#             unit = Meter.objects.get(id = int(self.pfc))
#             return u'%s' % (unit.meter_id)
#
#     unit_pfc = property(replace_pfc)
#
#     def __unicode__(self):
#         return self.title
#
#     # def save(self, produce_report=True, *args, **kwargs):
#     #     super(EnergyConsumptionReport, self).save(*args, **kwargs)
#     #     if produce_report:
#     #         self.produce_report()
#
#     # @override_timezone(pytz.timezone('CET'))
#     def produce_budget_report(self):
#         countryz = self.shedules.all()[0].country.country
#         # cet = pytz.timezone(timezone_country[str(countryz)])
#         cet = pytz.timezone('UTC')
#         print cet
#         print 'producing report'
#         _weekdays = [
#             'sunday', 'monday', 'tuesday',
#             'wednesday', 'thursday', 'friday', 'saturday'
#         ]
#         print 'DATA FROM = ', self.datetime_from, type(self.datetime_from)
#
#         # pfc_from = self.datetime_from
#         # pfc_to = self.datetime_to
#
#         pfc_from = make_aware(self.datetime_from.replace(tzinfo=None), cet, is_dst=None)
#         pfc_to = make_aware(self.datetime_to.replace(tzinfo=None), cet, is_dst=None)
#
#         print 'DATA pcf FROM = ', pfc_from, pfc_to
#
#         cet_dt_from = make_aware(
#             self.datetime_from.replace(tzinfo=None), cet, is_dst=None)
#
#         cet_dt_to = make_aware(
#             self.datetime_to.replace(tzinfo=None), cet, is_dst=None)
#
#
#         print cet_dt_from, cet_dt_to
#
#         records_lists = []
#         records_vlists = []
#         summary_dict = OrderedDict()
#         summary_dict_delay = OrderedDict()
#         holidays = Holiday.objects.filter(
#             country=self.budget.site.location.country,
#             region=self.budget.site.location.region,
#             date__gte=cet_dt_from.date(),
#             date__lte=cet_dt_to.date()
#         )
#
#         # All data from from PFC
#
#         pfc = Meter.objects.get(id = int(self.pfc))
#
#         print pfc
#         print self.unit
#
#         all_data = EnergyConsumptionRecord.objects.filter(
#             meter=pfc,
#             interval_start__gte=pfc_from,
#             interval_start__lte=pfc_to,
#             unit = self.unit
#         ).order_by('interval_start')
#
#
#         d_file = all_data.values('from_file')[0]
#         data_file = EnergyConsumptionFile.objects.get(id=d_file['from_file'])
#
#         first_holiday_year = str(cet_dt_from)[:4]
#         sec_holiday_year = str(cet_dt_to)[:4]
#
#         datas = all_data.values('interval_start', 'value').order_by('interval_start')
#
#
#         # All data from CC
#
#         cc_all_data = EnergyConsumptionRecord.objects.filter(
#             meter=self.budget,
#             interval_start__gte=cet_dt_from,
#             interval_start__lte=cet_dt_to
#         ).order_by('interval_start')
#
#         peak_data_rec_list = defaultdict(list)
#         peak_rec_data_res = []
#
#         cc_data = cc_all_data.values('interval_start', 'value')
#
#         d_meter = cc_data.values('meter')[0]
#         data_meter = Meter.objects.get(id=d_meter['meter'])
#         # print d_meter, data_meter.site
#
#         budget_meter, budget_created = Meter.objects.get_or_create(
#             meter_id='Budget_' + data_meter.meter_id + '_' + pfc.meter_id, site=data_meter.site)
#
#         # print 'budget created', budget_created
#
#         rec_list = []
#         for data in cc_data:
#             data_cc_cet = make_naive(data['interval_start'], pytz.timezone('UTC'))
#             rec_hour = str(data_cc_cet)[:13]
#             rec_list.append({rec_hour: data['value']})
#
#         #
#         # Sum per hour Peak values
#         #
#         for d in rec_list: # you can list as many input dicts as you want here
#             for key, value in d.iteritems():
#                 peak_data_rec_list[key].append(value)
#
#         for key in peak_data_rec_list.keys():
#             peak_rec_data_res.append({'value' : sum(item for item in peak_data_rec_list[key]) / 1000, 'interval_start' : key+':00'})
#
#         peak_rec_data_res = sorted(peak_rec_data_res, key=itemgetter('interval_start'))
#
#         peak_data = {}
#         for data in datas:
#             for k, v in data.items():
#                 if k == 'interval_start':
#                     data['interval_start'] = v.astimezone(cet)
#
#         print 'shedules = ', self.shedules.all()
#
#         months_all = [str(dt)[:7] for dt in rrule(MONTHLY, dtstart=cet_dt_from, until=cet_dt_to)]
#         # print months_all
#
#
#         # print 'datas from first meter ========= ', [d['value'] for d in datas]
#         # print 'datas from budget meter ========= ', [d['value'] for d in peak_rec_data_res]
#         # print 'dates ====== ', [d['interval_start'] for d in datas]
#
#         print len(datas), len(peak_rec_data_res)
#         # print 'PFC DATA = ', datas[1], datas[len(datas)-1]
#         # print 'CC DATA = ', peak_rec_data_res[1] ,peak_rec_data_res[len(peak_rec_data_res)-1]
#
#         rows = []
#         budget_data = [] # all produced budget
#         date_buget = []
#         cc_form_data = []
#         verfd = float(datas[100]['value'] * peak_rec_data_res[100]['value'])
#         bd_verify = EnergyConsumptionRecord.objects.filter(interval_start = datas[100]['interval_start'], value = verfd, meter=budget_meter).exists()
#         print 'dataaaaaa = ', bd_verify
#         for d in range(len(peak_rec_data_res)):
#             dateb = pytz.utc.localize(datetime.strptime(peak_rec_data_res[d]['interval_start'], '%Y-%m-%d %H:%M'))
#             date_buget.append(peak_rec_data_res[d]['interval_start'])
#             budget_data.append({'value' : datas[d]['value'] * peak_rec_data_res[d]['value'], 'cc' : peak_rec_data_res[d]['value'] * 1000, 'interval_start' : datas[d]['interval_start']})
#             # cc_form_data.append({'value' : peak_rec_data_res[d]['value']*1000, 'interval_start' : datas[d]['interval_start']})
#             # print 'pfc data', datas[d]['interval_start'], datas[d]['value'], 'cc data', peak_rec_data_res[d]['interval_start'], peak_rec_data_res[d]['value']
#             if bd_verify == False:
#                 # print 'create budget meter'
#                 record = EnergyConsumptionRecord(
#                     from_file=data_file,
#                     meter=budget_meter,
#                     value=float(datas[d]['value'] * peak_rec_data_res[d]['value']),
#                     interval_start=dateb,
#                     interval=timedelta(hours=1),
#                     unit=self.unit[:self.unit.index("/")]
#                 )
#                 rows.append(record)
#
#         EnergyConsumptionRecord.objects.bulk_create(rows)
#
#         shed_len_max = []
#         for sh in self.shedules.all() :
#             shed_len_max.append(len(sh.months.all().values_list('month', flat=True)))
#
#         output = StringIO.StringIO()
#         workbook = xlsxwriter.Workbook(output, {'in_memory': True})
#         worksheet = workbook.add_worksheet()
#
#         date_format = workbook.add_format({'num_format': 'm/d/yy'})
#         time_format = workbook.add_format({'num_format': 'hh:mm'})
#         scurt_format = workbook.add_format({'num_format': '0.000'})
#
#         text_format = workbook.add_format()
#         text_format.set_text_wrap()
#
#         # Widen column A for extra visibility.
#         worksheet.set_column('A:A', 10)
#         worksheet.set_column('B:B', 15)
#         worksheet.set_column('C:C', 15)
#         worksheet.set_column('P:P', 13)
#         chart = workbook.add_chart({'type': 'line'})
#         # Write some test data.
#         bold_format = workbook.add_format({'bold': True})
#         blue_format = workbook.add_format({'bold': True, 'color': 'blue'})
#
#         worksheet.write(0, 0, 'Report', bold_format)
#         worksheet.write(0, 1, self.title)
#
#
#         import calendar
#
#         sheet_col = {}
#         for i, month in enumerate(months_all):
#             worksheet.write(2, 3 + i, month)
#             sheet_col[month] = 3 + i
#             # worksheet.write(2, 3 + p, calendar.month_name[int(month)])
#
#
#         records = EnergyConsumptionRecord.objects.filter(
#             meter=self.budget,
#             interval_start__gte=cet_dt_from,
#             interval_start__lte=cet_dt_to
#         ).order_by('interval_start')
#         records_lists.append(records)
#
#         records = sorted(
#             unique_chain(*records_lists),
#             key=lambda instance: instance.interval_start
#         )
#
#
#         total = []
#         total_max = []
#
#         for index, shedule in enumerate(self.shedules.all()):
#             hourss = shedule.hours.all().values_list('value', flat=True)
#             months = shedule.months.all().values_list('month', flat=True)
#             weekdays = shedule.weekdays.all().values_list('day', flat=True)
#             weekend_days = shedule.weekend_days.all().values_list('day', flat=True)
#             hol = shedule.country.holidays.all().values_list('date', flat=True)
#             holiday_list = []
#
#             for v in hol:
#                 h = str(v)[:4]
#                 if h == first_holiday_year:
#                     holiday_list.append(v.isoformat())
#                 elif (first_holiday_year != sec_holiday_year and h == sec_holiday_year):
#                     holiday_list.append(v.isoformat())
#
#             #
#             # # Data cc
#             #
#
#             cc_data_list = []
#             peak_list = []
#             for data in budget_data:
#                 data_cet = make_naive(data['interval_start'], cet)
#                 weekday = int(datetime.strptime(str(data_cet)[:10], '%Y-%m-%d').isoweekday())
#                 hours = int(str(data_cet)[11:13])
#                 hour = time(int(str(data_cet)[11:13]), int(str(data_cet)[14:16]))
#                 day = str(data_cet)[:10]
#                 month_dic = str(data_cet)[:7]
#                 month = int(str(data_cet)[5:7])
#
#                 if ((hours in hourss) and (month in months) and (weekday in weekdays) and ((day not in holiday_list) == True)):
#                     peak_list.append({month_dic: data['value']})
#                     cc_data_list.append({month_dic: data['cc']})
#                     print 'Simple day = ', shedule.title, data_cet, month_dic, data['cc']
#
#                 if ((day in holiday_list) == True) and (shedule.holiday == True):
#                     if ((hours in hourss) and (month in months) and (weekday in weekdays)):
#                         peak_list.append({month_dic: data['value']})
#                         cc_data_list.append({month_dic: data['cc']})
#                         # print 'Holiday with first checkbox = ', shedule.title, data_cet, month_dic, data['value']
#                         print 'Holiday with first checkbox = ', shedule.title, data_cet, month_dic, data['cc']
#
#                 if ((weekday in weekend_days) and (month in months) and ((day in holiday_list) == True) and (shedule.weekend == True) and (shedule.holiday == True)):
#                     peak_list.append({month_dic: data['value']})
#                     cc_data_list.append({month_dic: data['cc']})
#                     # print 'Holiday as normal coincide cu weekend = ', shedule.title, data_cet, data['value']
#                     print 'Holiday as normal coincide cu weekend = ', shedule.title, data_cet, data['cc']
#
#                 if (((day in holiday_list) == True) and (month in months) and (shedule.all_holidays == True)):
#                     peak_list.append({month_dic: data['value']})
#                     cc_data_list.append({month_dic: data['cc']})
#                     # print shedule.title, shedule.all_holidays, 'All holidays ========== ', data['interval_start'], data['value']
#                     print shedule.title, shedule.all_holidays, 'All holidays ========== ', data['interval_start'], data['cc']
#
#                 if ((weekday in weekend_days) and (month in months) and ((day not in holiday_list) == True) and (shedule.weekend == True)):
#                     peak_list.append({month_dic: data['value']})
#                     cc_data_list.append({month_dic: data['cc']})
#                     # print shedule.title, shedule.weekend, 'All weekend data ========== ', data['interval_start'], data['value']
#                     print shedule.title, shedule.weekend, 'All weekend data ========== ', data['interval_start'], data['cc']
#
#
#             peak_data_list = defaultdict(list)
#             peak_data_res = []
#             peak_data_med_res = defaultdict(list)
#             peak_data_res_shedule = []
#             cc_data_med_res = defaultdict(list)
#             cc_data_res = defaultdict(list)
#             cc_data_res_shedule = []
#
#             #
#             # Media per month Peak values
#             #
#
#             for d in peak_list: # you can list as many input dicts as you want here
#                 for key, value in d.iteritems():
#                     peak_data_list[key].append(value)
#
#             for key in peak_data_list.keys():
#                 # peak_data_res.append({'month':key, 'max' : max(item for item in peak_data_list[key]), 'value' : sum(item for item in peak_data_list[key])/ len(peak_data_list[key])-1 })
#                 peak_data_res.append({'month':key, 'max' : max(item for item in peak_data_list[key]), 'lenght': len(peak_data_list[key])-1, 'value' : sum(item for item in peak_data_list[key])})
#
#             peak_data_res = sorted(peak_data_res, key=itemgetter('month'))
#
#
#             # print 'peak_rec_data_res ===== ', peak_rec_data_res
#
#             #
#             # Media Peak values
#             #
#
#             for key in peak_data_list.keys():
#                 peak_data_res_shedule += peak_data_list[key]
#                 month_med = datetime.strptime(key,'%Y-%m').month
#                 if month_med in [4,5,6,7,8,9]:
#                     peak_data_med_res['summer'] += peak_data_list[key]
#                 else :
#                     peak_data_med_res['winter'] += peak_data_list[key]
#
#             #
#             # Media CC values
#             #
#
#             for d in cc_data_list: # you can list as many input dicts as you want here
#                 for key, value in d.iteritems():
#                     cc_data_res[key].append(value)
#
#             for key in cc_data_res.keys():
#                 cc_data_res_shedule += cc_data_res[key]
#                 month_med = datetime.strptime(key,'%Y-%m').month
#                 if month_med in [4,5,6,7,8,9]:
#                     cc_data_med_res['summer'] += cc_data_res[key]
#                 else :
#                     cc_data_med_res['winter'] += cc_data_res[key]
#
#             print 'cc data med summer === ', float(sum(item for item in cc_data_med_res['summer']))
#             print 'cc data med winter === ', float(sum(item for item in cc_data_med_res['winter']))
#
#
#             print index, len(self.shedules.all())
#             # print shedule.title, ' result dictionary == ', peak_data_res
#
#             total_peak = 0
#             max_list = []
#
#             if records:
#                 worksheet.write(3, 2, 'MaxH', bold_format)
#                 worksheet.write(4+index, 2, shedule.title, bold_format)
#                 worksheet.write(9 + len(self.shedules.all()) + index, 8, shedule.title, bold_format)
#                 worksheet.write(9 + len(self.shedules.all()) + index, 9, sum(item for item in peak_data_med_res['summer']))
#                 worksheet.write(9 + len(self.shedules.all()) + index, 10, sum(item for item in peak_data_med_res['winter']))
#
#                 worksheet.write(13 + len(self.shedules.all()) , 9, 'Price per kWh', blue_format)
#                 worksheet.write(15 + len(self.shedules.all()) + index, 9, (sum(item for item in peak_data_med_res['summer'])/ float(str(sum(item for item in cc_data_med_res['summer'])))) * 100)
#                 worksheet.write(15 + len(self.shedules.all()) + index, 10, (sum(item for item in peak_data_med_res['winter'])/ float(str(sum(item for item in cc_data_med_res['winter'])))) * 100)
#
#
#                 # worksheet.write(20 + len(self.shedules.all()) + index, 9, float(str(sum(item for item in cc_data_med_res['summer']))))
#                 # worksheet.write(20 + len(self.shedules.all()) + index, 10, float(str(sum(item for item in cc_data_med_res['winter']))))
#
#                 for p, value in enumerate(peak_data_res):
#                     total_peak += value['value']
#                     worksheet.write(4+index, sheet_col[value['month']] , value['value'])
#                     total.append({value['month']: value['value']})
#                     total_max.append({value['month']: value['max']})
#
#                 worksheet.write(2, len(months_all)-1 + 4, 'Total', bold_format)
#                 worksheet.write(4 + index, len(months_all)-1 + 4, sum(item for item in peak_data_res_shedule) , scurt_format)
#
#
#         #
#         # Max for each month
#         #
#
#         total_max_data_list = defaultdict(list)
#         total_max_data_res = []
#
#         for d in total_max: # you can list as many input dicts as you want here
#             for key, value in d.iteritems():
#                 total_max_data_list[key].append(value)
#
#         for key in total_max_data_list.keys():
#             total_max_data_res.append({'month':key, 'max' : max(item for item in total_max_data_list[key])})
#
#         total_max_data_res = sorted(total_max_data_res, key=itemgetter('month'))
#         # print total_max_data_res
#         for p, m in enumerate(total_max_data_res):
#             worksheet.write(3, sheet_col[m['month']], m['max'])
#
#         # worksheet.write(3, len(months_all)-1 + 4, max(total_max_data_res, key=lambda x:x['max'])['max'], bold_format)
#         # worksheet.write(4 + len(self.shedules.all()), len(months_all)-1 + 4, total_months, bold_format)
#
#         worksheet.write(len(self.shedules.all()) + 8, 1, 'Date', bold_format)
#         worksheet.write(len(self.shedules.all()) + 8, 2, 'Time', bold_format)
#         worksheet.write(len(self.shedules.all()) + 8, 3, self.self_unit, bold_format)
#
#         # print 'peak days === ', [d['hour'][:10] for d in peak_rec_data_res]
#         # print 'peak hours === ', [d['hour'][11:13] for d in peak_rec_data_res]
#         # print 'peak values === ', [d['value'] for d in peak_rec_data_res]
#
#         worksheet.write_column('D'+ str(len(self.shedules.all()) + 10), [d['value'] for d in budget_data])
#         worksheet.write_column('B'+ str(len(self.shedules.all()) + 10), [str(d)[:10] for d in date_buget])
#         worksheet.write_column('C'+ str(len(self.shedules.all()) + 10), [str(d)[11:16] for d in date_buget])
#
#         #
#         # Average on summer and winter
#         #
#
#         worksheet.write(len(self.shedules.all()) + 8, 9, 'Summer', bold_format)
#         worksheet.write(len(self.shedules.all()) + 8, 10, 'Winter', bold_format)
#         worksheet.write(len(self.shedules.all()) + 14, 9, 'Summer', bold_format)
#         worksheet.write(len(self.shedules.all()) + 14, 10, 'Winter', bold_format)
#
#         workbook.close()
#
#         data_name = self.datetime_from
#         data_name_to = self.datetime_to
#
#         data = ContentFile(output.getvalue())
#         self.budget_file.save(
#             name='{}-{}-{}_{}_{}.xlsx'.format(self.budget.site.name, 'from', self.budget.site.company, data_name.strftime("%b%d-%Y"), data_name_to.strftime("%b%d-%Y")),
#             content=data,
#             save=False
#         )
#         self.save()
#

class EnergyConsumptionReport(TimeStampedModel):
    title = models.CharField(max_length=255)
    meter = models.ForeignKey('companies.Meter')
    time_peak = models.TimeField(blank=True, null=True)
    time_peakoff = models.TimeField(blank=True, null=True)
    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()
    unit = models.CharField(max_length=255, null=True)
    shedules = models.ManyToManyField(Shedule, related_name='shedules')
    periods = models.ManyToManyField(
        EnergyConsumptionPeriod, related_name='reports')
    result_file = models.FileField(null=True, blank=True)

    # def replace(self):
    #     return self.unit.replace('/', '_')

    def replace(self):
        if self.unit != None:
            unit = self.unit
            return u'%s' % (unit.replace('/', '_'))

    unit_rep = property(replace)

    def __unicode__(self):
        return self.title


    # def save(self, produce_report=True, *args, **kwargs):
    #     super(EnergyConsumptionReport, self).save(*args, **kwargs)
    #     if produce_report:
    #         self.produce_report()

    # @override_timezone(pytz.timezone('CET'))
    def produce_cc_report(self):
        countryz = self.shedules.all()[0].country.country
        # cet = pytz.timezone(timezone_country[str(countryz)])
        cet = pytz.timezone('UTC')
        print cet
        print 'producing report'
        _weekdays = [
            'sunday', 'monday', 'tuesday',
            'wednesday', 'thursday', 'friday', 'saturday'
        ]
        # print 'DATA FROM = ', self.datetime_from, type(self.datetime_from)

        cet_dt_from = make_aware(
            self.datetime_from.replace(tzinfo=None), cet, is_dst=None)

        cet_dt_to = make_aware(
            self.datetime_to.replace(tzinfo=None), cet, is_dst=None)
        records_lists = []
        records_vlists = []
        summary_dict = OrderedDict()
        summary_dict_delay = OrderedDict()
        holidays = Holiday.objects.filter(
            country=self.meter.site.location.country,
            region=self.meter.site.location.region,
            date__gte=cet_dt_from.date(),
            date__lte=cet_dt_to.date()
        )

        all_data = EnergyConsumptionRecord.objects.filter(
            meter=self.meter,
            interval_start__gte=cet_dt_from,
            interval_start__lte=cet_dt_to,
            unit = str(self.unit)
        ).order_by('interval_start')


        first_holiday_year = str(cet_dt_from)[:4]
        sec_holiday_year = str(cet_dt_to)[:4]

        datas = all_data.values('interval_start', 'value')
        unit = all_data.values('unit')[0]
        # if self.unit == None :
        #     self.unit = unit['unit']

        peak_data = {}

        for data in datas:
            for k, v in data.items():
                if k == 'interval_start':
                    data['interval_start'] = v.astimezone(cet)

        print 'shedules = ', self.shedules.all()

        months_all = [str(dt)[:7] for dt in rrule(MONTHLY, dtstart=cet_dt_from, until=cet_dt_to)]
        print months_all

        # shed_len_max = []
        # for sh in self.shedules.all() :
        #     shed_len_max.append(len(sh.months.all().values_list('month', flat=True)))

        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        date_format = workbook.add_format({'num_format': 'm/d/yy'})
        time_format = workbook.add_format({'num_format': 'hh:mm'})
        scurt_format = workbook.add_format({'num_format': '0.00'})
        cc_format = workbook.add_format({'num_format': '#.##'})

        # Widen column A for extra visibility.
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('P:P', 13)
        chart = workbook.add_chart({'type': 'line'})
        # Write some test data.
        bold_format = workbook.add_format({'bold': True})

        worksheet.write(0, 0, 'Report', bold_format)
        worksheet.write(0, 1, self.meter.site.name)


        import calendar

        sheet_col = {}
        for i, month in enumerate(months_all):
            worksheet.write(2, 3 + i, month)
            sheet_col[month] = 3 + i
            # worksheet.write(2, 3 + p, calendar.month_name[int(month)])

        records = EnergyConsumptionRecord.objects.filter(
            meter=self.meter,
            interval_start__gte=cet_dt_from,
            interval_start__lte=cet_dt_to,
            unit = self.unit
        ).order_by('interval_start')
        records_lists.append(records)

        records = sorted(
            unique_chain(*records_lists),
            key=lambda instance: instance.interval_start
        )

        records_value = EnergyConsumptionRecord.objects.filter(
            meter=self.meter,
            interval_start__gte=cet_dt_from,
            interval_start__lte=cet_dt_to,
            unit = self.unit
        ).order_by('interval_start').values_list('value', flat=True)


        records_interval = EnergyConsumptionRecord.objects.filter(
            meter=self.meter,
            interval_start__gte=cet_dt_from,
            interval_start__lte=cet_dt_to,
            unit = self.unit
        ).order_by('interval_start').values_list('interval_start', flat=True)

        records_hours = []

        total = []
        total_max = []
        weekly = []

        for index, shedule in enumerate(self.shedules.all()):
            hourss = shedule.hours.all().values_list('value', flat=True)
            months = shedule.months.all().values_list('month', flat=True)
            weekdays = shedule.weekdays.all().values_list('day', flat=True)
            weekend_days = shedule.weekend_days.all().values_list('day', flat=True)
            hol = shedule.country.holidays.all().values_list('date', flat=True)
            holiday_list = []

            for v in hol:
                h = str(v)[:4]
                if h == first_holiday_year:
                    holiday_list.append(v.isoformat())
                elif (first_holiday_year != sec_holiday_year and h == sec_holiday_year):
                    holiday_list.append(v.isoformat())

            rec_list = []
            peak_list = []
            for data in datas:
                data_cet = make_naive(data['interval_start'], cet)
                weekday = int(datetime.strptime(str(data_cet)[:10], '%Y-%m-%d').isoweekday())
                hours = int(str(data_cet)[11:13])
                hour = time(int(str(data_cet)[11:13]), int(str(data_cet)[14:16]))
                day = str(data_cet)[:10]
                month_dic = str(data_cet)[:7]
                month = int(str(data_cet)[5:7])
                rec_hour = str(data_cet)[:13]
                rec_list.append({rec_hour: data['value']})

                if ((hours in hourss) and (month in months) and (weekday in weekdays) and ((day not in holiday_list) == True)):
                    peak_list.append({month_dic: data['value']})

                if ((day in holiday_list) == True) and (shedule.holiday == True):
                    if ((hours in hourss) and (month in months) and (weekday in weekdays)):
                        peak_list.append({month_dic: data['value']})
                        # print 'Holiday with first checkbox = ', shedule.title, data_cet, month_dic, data['value']

                if ((weekday in weekend_days) and (month in months) and ((day in holiday_list) == True) and (shedule.weekend == True) and (shedule.holiday == True)):
                    peak_list.append({month_dic: data['value']})
                    # print 'Holiday as normal coincide cu weekend = ', shedule.title, data_cet, data['value']

                if (((day in holiday_list) == True) and (month in months) and (shedule.all_holidays == True)):
                    peak_list.append({month_dic: data['value']})
                    # print shedule.title, shedule.all_holidays, 'All holidays ========== ', data['interval_start'], data['value']

                if ((weekday in weekend_days) and (month in months) and ((day not in holiday_list) == True) and (shedule.weekend == True)):
                    peak_list.append({month_dic: data['value']})
                    # print shedule.title, shedule.weekend, 'All weekend data ========== ', data['interval_start'], data['value']


            peak_data_list = defaultdict(list)
            peak_data_rec_list = defaultdict(list)
            peak_data_res = []
            peak_rec_data_res = []
            peak_data_med_res = defaultdict(list)
            peak_data_res_shedule = []
            #
            # Sum per month Peak values
            #

            for d in peak_list: # you can list as many input dicts as you want here
                for key, value in d.iteritems():
                    peak_data_list[key].append(value)


            for key in peak_data_list.keys():
                # peak_data_res.append({'month':key, 'max' : max(item for item in peak_data_list[key]), 'value' : sum(item for item in peak_data_list[key])/ len(peak_data_list[key])-1 })
                peak_data_res.append({'month':key, 'max' : max(item for item in peak_data_list[key]), 'lenght': len(peak_data_list[key])-1, 'value' : sum(item for item in peak_data_list[key])})

            peak_data_res = sorted(peak_data_res, key=itemgetter('month'))


            #
            # Sum per hour Peak values
            #

            # print 'data pe hour = ', rec_list

            for d in rec_list: # you can list as many input dicts as you want here
                for key, value in d.iteritems():
                    peak_data_rec_list[key].append(value)

            for key in peak_data_rec_list.keys():
                weekday = int(datetime.strptime(key[:10], '%Y-%m-%d').isoweekday())
                hour = int(str(key)[11:13])
                peak_rec_data_res.append({'hour':key+':00', 'value' : sum(item for item in peak_data_rec_list[key])})
                # weekly.append({'hour':key+':00', 'weekhour': (weekday-1)*24+hour, 'value' : sum(item for item in peak_data_rec_list[key])})
                weekly.append({(weekday-1)*24+hour: sum(item for item in peak_data_rec_list[key])})
                # print 'hour = ', key, 'weekhour', (weekday-1)*24+hour, 'value' , sum(item for item in peak_data_rec_list[key])


            peak_rec_data_res = sorted(peak_rec_data_res, key=itemgetter('hour'))

            # print 'peak_rec_data_res ===== ', peak_rec_data_res

            #
            # Media Peak values
            #

            for key in peak_data_list.keys():
                peak_data_res_shedule += peak_data_list[key]
                month_med = datetime.strptime(key,'%Y-%m').month
                if month_med in [4,5,6,7,8,9]:
                    peak_data_med_res['summer'] += peak_data_list[key]
                else :
                    peak_data_med_res['winter'] += peak_data_list[key]


            # print index, len(self.shedules.all())
            # print shedule.title, ' result dictionary == ', peak_data_res

            total_peak = 0
            max_list = []

            if records:
                summer = float(str(sum(item for item in peak_data_med_res['summer'])))
                winter = float(str(sum(item for item in peak_data_med_res['winter'])))
                worksheet.write(3, 2, 'Pmax', bold_format)
                worksheet.write(4+index, 2, shedule.title, bold_format)
                worksheet.write(9 + len(self.shedules.all()) + index, 8, shedule.title, bold_format)
                worksheet.write(9 + len(self.shedules.all()) + index, 9, summer)
                worksheet.write(9 + len(self.shedules.all()) + index, 10, winter)

                print 'summer == ', sum(item for item in peak_data_med_res['summer'])
                print 'winter == ', sum(item for item in peak_data_med_res['winter'])


                for p, value in enumerate(peak_data_res):
                    total_peak += value['value']
                    worksheet.write(4+index, sheet_col[value['month']] , value['value'])
                    total.append({value['month']: value['value']})
                    total_max.append({value['month']: value['max']})

                worksheet.write(2, len(months_all)-1 + 4, 'Total', bold_format)
                worksheet.write(4 + index, len(months_all)-1 + 4, total_peak, bold_format)

                # worksheet.write(4 + index, len(months_all)-1 + 4, sum(item for item in peak_data_res_shedule) , scurt_format)

        worksheet.write(4 + len(self.shedules.all()), 2, 'Total(kWh)', bold_format)

        #
        # Media data by weekly hour
        #
        # print weekly

        weekly_list = defaultdict(list)
        weekly_res = []
        for d in weekly: # you can list as many input dicts as you want here
            for key, value in d.iteritems():
                weekly_list[key].append(value)

        for key in weekly_list.keys():
            weekly_res.append({'hour':key, 'value' : sum(item for item in weekly_list[key])/ len(weekly_list[key])})

        weekly_res = sorted(weekly_res, key=itemgetter('hour'))
        # print 'data per weekely hour ==== ', weekly_res


        #
        # Total for each month
        #

        total_data_list = defaultdict(list)
        total_data_res = []
        for d in total: # you can list as many input dicts as you want here
            for key, value in d.iteritems():
                total_data_list[key].append(value)

        for key in total_data_list.keys():
            total_data_res.append({'month':key, 'total' : sum(item for item in total_data_list[key])})

        total_data_res = sorted(total_data_res, key=itemgetter('month'))
        # print total_data_res

        total_months = 0
        for p, t in enumerate(total_data_res):
            total_months+=t['total']
            worksheet.write(4 + len(self.shedules.all()), sheet_col[t['month']], t['total'], bold_format)

        #
        # Max for each month
        #

        total_max_data_list = defaultdict(list)
        total_max_data_res = []

        for d in total_max: # you can list as many input dicts as you want here
            for key, value in d.iteritems():
                total_max_data_list[key].append(value)

        for key in total_max_data_list.keys():
            total_max_data_res.append({'month':key, 'max' : max(item for item in total_max_data_list[key])})

        total_max_data_res = sorted(total_max_data_res, key=itemgetter('month'))
        # print total_max_data_res
        for p, m in enumerate(total_max_data_res):
            worksheet.write(3, sheet_col[m['month']], m['max'] * 4)

        worksheet.write(3, len(months_all)-1 + 4, max(total_max_data_res, key=lambda x:x['max'])['max'] * 4, bold_format)
        worksheet.write(4 + len(self.shedules.all()), len(months_all)-1 + 4, total_months, bold_format)

        worksheet.write(len(self.shedules.all()) + 8, 1, 'Date', bold_format)
        worksheet.write(len(self.shedules.all()) + 8, 2, 'Time', bold_format)
        worksheet.write(len(self.shedules.all()) + 8, 3, unit['unit'], bold_format)

        worksheet.write(len(self.shedules.all()) + 8, 14, 'Weekly day', bold_format)
        worksheet.write(len(self.shedules.all()) + 8, 15, 'Average value', bold_format)

        # print 'peak days === ', [d['hour'][:10] for d in peak_rec_data_res]
        # print 'peak hours === ', [d['hour'][11:13] for d in peak_rec_data_res]
        # print 'peak values === ', [d['value'] for d in peak_rec_data_res]

        worksheet.write_column('D'+ str(len(self.shedules.all()) + 10), [d['value'] for d in peak_rec_data_res])
        worksheet.write_column('B'+ str(len(self.shedules.all()) + 10), [d['hour'][:10] for d in peak_rec_data_res])
        worksheet.write_column('C'+ str(len(self.shedules.all()) + 10), [d['hour'][11:16] for d in peak_rec_data_res])


        worksheet.write_column('O'+ str(len(self.shedules.all()) + 10), [d['hour'] for d in weekly_res])
        worksheet.write_column('P'+ str(len(self.shedules.all()) + 10), [d['value'] for d in weekly_res])
        #
        # Average on summer and winter
        #

        worksheet.write(len(self.shedules.all()) + 8, 9, 'Summer', bold_format)
        worksheet.write(len(self.shedules.all()) + 8, 10, 'Winter', bold_format)


        workbook.close()

        data_name = self.datetime_from
        data_name_to = self.datetime_to

        data = ContentFile(output.getvalue())
        self.result_file.save(
            name='{}-{}-{}_{}_{}.xlsx'.format(self.meter.site.name, 'from', self.meter.site.company, data_name.strftime("%b%d-%Y"), data_name_to.strftime("%b%d-%Y")),
            content=data,
            save=False
        )
        self.save()


    # @override_timezone(pytz.timezone('CET'))
    def produce_pfc_report(self):
        countryz = self.shedules.all()[0].country.country
        # cet = pytz.timezone(timezone_country[str(countryz)])
        cet = pytz.timezone('UTC')
        print cet
        print 'producing report'
        _weekdays = [
            'sunday', 'monday', 'tuesday',
            'wednesday', 'thursday', 'friday', 'saturday'
        ]
        # print 'DATA FROM = ', self.datetime_from, type(self.datetime_from)

        cet_dt_from = make_aware(
            self.datetime_from.replace(tzinfo=None), cet, is_dst=None)

        cet_dt_to = make_aware(
            self.datetime_to.replace(tzinfo=None), cet, is_dst=None)
        records_lists = []
        records_vlists = []
        summary_dict = OrderedDict()
        summary_dict_delay = OrderedDict()
        holidays = Holiday.objects.filter(
            country=self.meter.site.location.country,
            region=self.meter.site.location.region,
            date__gte=cet_dt_from.date(),
            date__lte=cet_dt_to.date()
        )

        all_data = EnergyConsumptionRecord.objects.filter(
            meter=self.meter,
            interval_start__gte=cet_dt_from,
            interval_start__lte=cet_dt_to,
            unit = self.unit,
        ).order_by('interval_start')

        print all_data


        first_holiday_year = str(cet_dt_from)[:4]
        sec_holiday_year = str(cet_dt_to)[:4]

        datas = all_data.values('interval_start', 'value')
        unit = all_data.values('unit')[0]

        peak_data = {}

        for data in datas:
            for k, v in data.items():
                if k == 'interval_start':
                    data['interval_start'] = v.astimezone(cet)

        print 'shedules = ', self.shedules.all()

        months_all = [str(dt)[:7] for dt in rrule(MONTHLY, dtstart=cet_dt_from, until=cet_dt_to)]
        print months_all

        # shed_len_max = []
        # for sh in self.shedules.all() :
        #     shed_len_max.append(len(sh.months.all().values_list('month', flat=True)))

        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        date_format = workbook.add_format({'num_format': 'm/d/yy'})
        time_format = workbook.add_format({'num_format': 'hh:mm'})
        scurt_format = workbook.add_format({'num_format': '#.####'})

        # Widen column A for extra visibility.
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('P:P', 13)
        chart = workbook.add_chart({'type': 'line'})
        # Write some test data.
        bold_format = workbook.add_format({'bold': True})

        worksheet.write(0, 0, 'Report', bold_format)
        worksheet.write(0, 1, self.meter.site.name)


        import calendar

        sheet_col = {}
        for i, month in enumerate(months_all):
            worksheet.write(2, 3 + i, month)
            sheet_col[month] = 3 + i
            # worksheet.write(2, 3 + p, calendar.month_name[int(month)])

        records = EnergyConsumptionRecord.objects.filter(
            meter=self.meter,
            interval_start__gte=cet_dt_from,
            interval_start__lte=cet_dt_to,
            unit = self.unit,
        ).order_by('interval_start')
        records_lists.append(records)

        records = sorted(
            unique_chain(*records_lists),
            key=lambda instance: instance.interval_start
        )

        records_value = EnergyConsumptionRecord.objects.filter(
            meter=self.meter,
            interval_start__gte=cet_dt_from,
            interval_start__lte=cet_dt_to,
            unit = self.unit,
        ).order_by('interval_start').values_list('value', flat=True)


        records_interval = EnergyConsumptionRecord.objects.filter(
            meter=self.meter,
            interval_start__gte=cet_dt_from,
            interval_start__lte=cet_dt_to,
            unit = self.unit,
        ).order_by('interval_start').values_list('interval_start', flat=True)

        records_hours = []
        for r in records_interval:
            records_vlists.append(str(make_naive(r, cet))[:10])
            records_hours.append(str(make_naive(r, cet))[11:16])

        total = []
        total_max = []

        for index, shedule in enumerate(self.shedules.all()):
            hourss = shedule.hours.all().values_list('value', flat=True)
            months = shedule.months.all().values_list('month', flat=True)
            weekdays = shedule.weekdays.all().values_list('day', flat=True)
            weekend_days = shedule.weekend_days.all().values_list('day', flat=True)
            hol = shedule.country.holidays.all().values_list('date', flat=True)
            holiday_list = []

            for v in hol:
                h = str(v)[:4]
                if h == first_holiday_year:
                    holiday_list.append(v.isoformat())
                elif (first_holiday_year != sec_holiday_year and h == sec_holiday_year):
                    holiday_list.append(v.isoformat())

            peak_list = []
            for data in datas:
                data_cet = make_naive(data['interval_start'], cet)
                weekday = int(datetime.strptime(str(data_cet)[:10], '%Y-%m-%d').isoweekday())
                hours = int(str(data_cet)[11:13])
                hour = time(int(str(data_cet)[11:13]), int(str(data_cet)[14:16]))
                day = str(data_cet)[:10]
                month_dic = str(data_cet)[:7]
                month = int(str(data_cet)[5:7])
                # print 'All Holidays = ', shedule.all_holidays
                # print 'Holiday = ', shedule.holiday
                # print 'Day holiday = ', day in holiday_list

                if ((hours in hourss) and (month in months) and (weekday in weekdays) and ((day not in holiday_list) == True)):
                    peak_list.append({month_dic: data['value']})

                if ((day in holiday_list) == True) and (shedule.holiday == True):
                    if ((hours in hourss) and (month in months) and (weekday in weekdays)):
                        peak_list.append({month_dic: data['value']})
                        # print 'Holiday with first checkbox = ', shedule.title, data_cet, month_dic, data['value']

                if ((weekday in weekend_days) and (month in months) and ((day in holiday_list) == True) and (shedule.weekend == True) and (shedule.holiday == True)):
                    peak_list.append({month_dic: data['value']})
                    # print 'Holiday as normal coincide cu weekend = ', shedule.title, data_cet, data['value']

                if (((day in holiday_list) == True) and (month in months) and (shedule.all_holidays == True)):
                    peak_list.append({month_dic: data['value']})
                    # print shedule.title, shedule.all_holidays, 'All holidays ========== ', data['interval_start'], data['value']

                if ((weekday in weekend_days) and (month in months) and ((day not in holiday_list) == True) and (shedule.weekend == True)):
                    peak_list.append({month_dic: data['value']})
                    # print shedule.title, shedule.weekend, 'All weekend data ========== ', data['interval_start'], data['value']


            from collections import defaultdict
            from operator import itemgetter

            peak_data_list = defaultdict(list)
            peak_data_res = []
            peak_data_med_res = defaultdict(list)
            peak_data_res_shedule = []
            #
            # Media per month Peak values
            #

            for d in peak_list: # you can list as many input dicts as you want here
                for key, value in d.iteritems():
                    peak_data_list[key].append(value)

            for key in peak_data_list.keys():
                peak_data_res.append({'month':key, 'max' : max(item for item in peak_data_list[key]), 'value' : sum(item for item in peak_data_list[key])/ float(len(peak_data_list[key])-1) })

            peak_data_res = sorted(peak_data_res, key=itemgetter('month'))

            #
            # Media Peak values
            #

            for key in peak_data_list.keys():
                peak_data_res_shedule += peak_data_list[key]
                month_med = datetime.strptime(key,'%Y-%m').month
                if month_med in [4,5,6,7,8,9]:
                    peak_data_med_res['summer'] += peak_data_list[key]
                else :
                    peak_data_med_res['winter'] += peak_data_list[key]


            print index, len(self.shedules.all())
            print shedule.title, ' result dictionary == ', peak_data_res

            total_peak = 0
            max_list = []

            if records:
                worksheet.write(3, 2, 'Max', bold_format)
                worksheet.write(4+index, 2, shedule.title, bold_format)
                worksheet.write(9 + len(self.shedules.all()) + index, 8, shedule.title, bold_format)
                worksheet.write(9 + len(self.shedules.all()) + index, 9, sum(item for item in peak_data_med_res['summer'])/float(len(peak_data_med_res['summer'])-1))
                worksheet.write(9 + len(self.shedules.all()) + index, 10, sum(item for item in peak_data_med_res['winter'])/float(len(peak_data_med_res['winter'])-1))


                for p, value in enumerate(peak_data_res):
                    total_peak += value['value']
                    worksheet.write(4+index, sheet_col[value['month']] , value['value'])
                    total.append({value['month']: value['value']})
                    total_max.append({value['month']: value['max']})

                worksheet.write(2, len(months_all)-1 + 4, 'Anual Average', bold_format)
                worksheet.write(4 + index, len(months_all)-1 + 4, sum(item for item in peak_data_res_shedule)/float(len(peak_data_res_shedule)-1) , scurt_format)


        #
        # Total for each month
        #

        # total_data_list = defaultdict(list)
        # total_data_res = []
        # for d in total: # you can list as many input dicts as you want here
        #     for key, value in d.iteritems():
        #         total_data_list[key].append(value)
        #
        # for key in total_data_list.keys():
        #     total_data_res.append({'month':key, 'total' : sum(item for item in total_data_list[key])})
        #
        # total_data_res = sorted(total_data_res, key=itemgetter('month'))
        # print total_data_res
        # total_months = 0
        # for p, t in enumerate(total_data_res):
        #     total_months+=t['total']

        #
        # Max for each month
        #

        total_max_data_list = defaultdict(list)
        total_max_data_res = []

        for d in total_max: # you can list as many input dicts as you want here
            for key, value in d.iteritems():
                total_max_data_list[key].append(value)

        for key in total_max_data_list.keys():
            total_max_data_res.append({'month':key, 'max' : max(item for item in total_max_data_list[key])})

        total_max_data_res = sorted(total_max_data_res, key=itemgetter('month'))
        print total_max_data_res
        for p, m in enumerate(total_max_data_res):
            worksheet.write(3, sheet_col[m['month']], m['max'])

        # worksheet.write(3, len(months_all)-1 + 4, max(total_max_data_res, key=lambda x:x['max'])['max'], bold_format)
        # worksheet.write(4 + len(self.shedules.all()), len(months_all)-1 + 4, total_months, bold_format)

        worksheet.write(len(self.shedules.all()) + 8, 1, 'Date', bold_format)
        worksheet.write(len(self.shedules.all()) + 8, 2, 'Time', bold_format)
        worksheet.write(len(self.shedules.all()) + 8, 3, unit['unit'], bold_format)

        worksheet.write_column('D'+ str(len(self.shedules.all()) + 10), records_value)
        worksheet.write_column('B'+ str(len(self.shedules.all()) + 10), records_vlists)
        worksheet.write_column('C'+ str(len(self.shedules.all()) + 10), records_hours)

        #
        # Average on summer and winter
        #

        worksheet.write(len(self.shedules.all()) + 8, 9, 'Summer', bold_format)
        worksheet.write(len(self.shedules.all()) + 8, 10, 'Winter', bold_format)


        workbook.close()

        data_name = self.datetime_from
        data_name_to = self.datetime_to

        data = ContentFile(output.getvalue())
        self.result_file.save(
            name='{}-{}-{}_{}_{}.xlsx'.format(self.meter.site.name, 'from', self.meter.site.company, data_name.strftime("%b%d-%Y"), data_name_to.strftime("%b%d-%Y")),
            content=data,
            save=False
        )
        self.save()


    # @override_timezone(pytz.timezone('CET'))
    def produce_report(self):
        countryz = self.shedules.all()[0].country.country
        cet = pytz.timezone(timezone_country[str(countryz)])
        # cet = pytz.timezone('CET')
        print cet
        print 'producing report'
        _weekdays = [
            'sunday', 'monday', 'tuesday',
            'wednesday', 'thursday', 'friday', 'saturday'
        ]
        # print 'DATA FROM = ', self.datetime_from, type(self.datetime_from)

        cet_dt_from = make_aware(
            self.datetime_from.replace(tzinfo=None), cet, is_dst=None)

        cet_dt_to = make_aware(
            self.datetime_to.replace(tzinfo=None), cet, is_dst=None)
        records_lists = []
        records_vlists = []
        summary_dict = OrderedDict()
        summary_dict_delay = OrderedDict()
        holidays = Holiday.objects.filter(
            country=self.meter.site.location.country,
            region=self.meter.site.location.region,
            date__gte=cet_dt_from.date(),
            date__lte=cet_dt_to.date()
        )

        all_data = EnergyConsumptionRecord.objects.filter(
            meter=self.meter,
            interval_start__gte=cet_dt_from,
            interval_start__lte=cet_dt_to
        ).order_by('interval_start')


        first_holiday_year = str(cet_dt_from)[:4]
        sec_holiday_year = str(cet_dt_to)[:4]

        datas = all_data.values('interval_start', 'value')

        peak_data = {}

        for data in datas:
            for k, v in data.items():
                if k == 'interval_start':
                    data['interval_start'] = v.astimezone(cet)

        print 'shedules = ', self.shedules.all()

        months_all = [str(dt)[:7] for dt in rrule(MONTHLY, dtstart=cet_dt_from, until=cet_dt_to)]
        print months_all

        # shed_len_max = []
        # for sh in self.shedules.all() :
        #     shed_len_max.append(len(sh.months.all().values_list('month', flat=True)))

        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        date_format = workbook.add_format({'num_format': 'm/d/yy'})
        time_format = workbook.add_format({'num_format': 'hh:mm'})

        # Widen column A for extra visibility.
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 10)
        chart = workbook.add_chart({'type': 'line'})
        # Write some test data.
        bold_format = workbook.add_format({'bold': True})

        worksheet.write(0, 0, 'Site Name', bold_format)
        worksheet.write(0, 1, self.meter.site.name)

        worksheet.write(1, 0, 'Meter ID', bold_format)
        worksheet.write(1, 1, self.meter.meter_id)

        import calendar

        sheet_col = {}
        for i, month in enumerate(months_all):
            worksheet.write(2, 3 + i, month)
            sheet_col[month] = 3 + i
            # worksheet.write(2, 3 + p, calendar.month_name[int(month)])

        records = EnergyConsumptionRecord.objects.filter(
            meter=self.meter,
            interval_start__gte=cet_dt_from,
            interval_start__lte=cet_dt_to
        ).order_by('interval_start')
        records_lists.append(records)

        records = sorted(
            unique_chain(*records_lists),
            key=lambda instance: instance.interval_start
        )

        records_value = EnergyConsumptionRecord.objects.filter(
            meter=self.meter,
            interval_start__gte=cet_dt_from,
            interval_start__lte=cet_dt_to
        ).order_by('interval_start').values_list('value', flat=True)


        records_interval = EnergyConsumptionRecord.objects.filter(
            meter=self.meter,
            interval_start__gte=cet_dt_from,
            interval_start__lte=cet_dt_to
        ).order_by('interval_start').values_list('interval_start', flat=True)

        records_hours = []
        for r in records_interval:
            records_vlists.append(str(make_naive(r, cet))[:10])
            records_hours.append(str(make_naive(r, cet))[11:16])

        total = []
        total_max = []

        for index, shedule in enumerate(self.shedules.all()):
            hourss = shedule.hours.all().values_list('value', flat=True)
            months = shedule.months.all().values_list('month', flat=True)
            weekdays = shedule.weekdays.all().values_list('day', flat=True)
            weekend_days = shedule.weekend_days.all().values_list('day', flat=True)
            hol = shedule.country.holidays.all().values_list('date', flat=True)
            holiday_list = []

            for v in hol:
                h = str(v)[:4]
                if h == first_holiday_year:
                    holiday_list.append(v.isoformat())
                elif (first_holiday_year != sec_holiday_year and h == sec_holiday_year):
                    holiday_list.append(v.isoformat())

            peak_list = []
            for data in datas:
                data_cet = make_naive(data['interval_start'], cet)
                weekday = int(datetime.strptime(str(data_cet)[:10], '%Y-%m-%d').isoweekday())
                hours = int(str(data_cet)[11:13])
                hour = time(int(str(data_cet)[11:13]), int(str(data_cet)[14:16]))
                day = str(data_cet)[:10]
                month_dic = str(data_cet)[:7]
                month = int(str(data_cet)[5:7])
                # print 'All Holidays = ', shedule.all_holidays
                # print 'Holiday = ', shedule.holiday
                # print 'Day holiday = ', day in holiday_list

                if ((hours in hourss) and (month in months) and (weekday in weekdays) and ((day not in holiday_list) == True)):
                    peak_list.append({month_dic: data['value']})

                if ((day in holiday_list) == True) and (shedule.holiday == True):
                    if ((hours in hourss) and (month in months) and (weekday in weekdays)):
                        peak_list.append({month_dic: data['value']})
                        # print 'Holiday with first checkbox = ', shedule.title, data_cet, month_dic, data['value']

                #?????????????
                if ((weekday in weekend_days) and (month in months) and ((day in holiday_list) == True) and (shedule.weekend == True) and (shedule.holiday == True)):
                    peak_list.append({month_dic: data['value']})
                    # print 'Holiday as normal coincide cu weekend = ', shedule.title, data_cet, data['value']
                #????????????

                if (((day in holiday_list) == True) and (month in months) and (shedule.all_holidays == True)):
                    peak_list.append({month_dic: data['value']})
                    # print shedule.title, shedule.all_holidays, 'All holidays ========== ', data['interval_start'], data['value']

                if ((weekday in weekend_days) and (month in months) and ((day not in holiday_list) == True) and (shedule.weekend == True)):
                    peak_list.append({month_dic: data['value']})
                    # print shedule.title, shedule.weekend, 'All weekend data ========== ', data['interval_start'], data['value']


            from collections import defaultdict
            from operator import itemgetter

            peak_data_list = defaultdict(list)
            peak_data_res = []

            #
            # Sum Peak values
            #

            for d in peak_list: # you can list as many input dicts as you want here
                for key, value in d.iteritems():
                    peak_data_list[key].append(value)

            for key in peak_data_list.keys():
                peak_data_res.append({'month':key, 'max' : max(item for item in peak_data_list[key]), 'value' : sum(item for item in peak_data_list[key]) / 4 / 1000})
                # print key, 'peak sum ==',  sum(item for item in peak_data_list[key])  / 4 / 1000

            peak_data_res = sorted(peak_data_res, key=itemgetter('month'))
            print index, len(self.shedules.all())
            print shedule.title, ' result dictionary == ', peak_data_res

            total_peak = 0
            max_list = []

            if records:
                worksheet.write(3, 2, 'Max(kW)', bold_format)
                worksheet.write(4+index, 2, shedule.title, bold_format)

                for p, value in enumerate(peak_data_res):
                    total_peak += value['value']
                    worksheet.write(4+index, sheet_col[value['month']] , value['value'])
                    total.append({value['month']: value['value']})
                    total_max.append({value['month']: value['max']})

                worksheet.write(2, len(months_all)-1 + 4, 'Total', bold_format)
                worksheet.write(4 + index, len(months_all)-1 + 4, total_peak, bold_format)

        worksheet.write(4 + len(self.shedules.all()), 2, 'Total(MWh)', bold_format)

        #
        # Total for each month
        #

        total_data_list = defaultdict(list)
        total_data_res = []
        for d in total: # you can list as many input dicts as you want here
            for key, value in d.iteritems():
                total_data_list[key].append(value)

        for key in total_data_list.keys():
            total_data_res.append({'month':key, 'total' : sum(item for item in total_data_list[key])})

        total_data_res = sorted(total_data_res, key=itemgetter('month'))
        print total_data_res

        total_months = 0
        for p, t in enumerate(total_data_res):
            total_months+=t['total']
            worksheet.write(4 + len(self.shedules.all()), sheet_col[t['month']], t['total'], bold_format)

        #
        # Max for each month
        #

        total_max_data_list = defaultdict(list)
        total_max_data_res = []

        for d in total_max: # you can list as many input dicts as you want here
            for key, value in d.iteritems():
                total_max_data_list[key].append(value)

        for key in total_max_data_list.keys():
            total_max_data_res.append({'month':key, 'max' : max(item for item in total_max_data_list[key])})

        total_max_data_res = sorted(total_max_data_res, key=itemgetter('month'))
        print total_max_data_res
        for p, m in enumerate(total_max_data_res):
            worksheet.write(3, sheet_col[m['month']], m['max'])

        worksheet.write(3, len(months_all)-1 + 4, max(total_max_data_res, key=lambda x:x['max'])['max'], bold_format)
        worksheet.write(4 + len(self.shedules.all()), len(months_all)-1 + 4, total_months, bold_format)



        worksheet.write(len(self.shedules.all()) + 8, 1, 'Date', bold_format)
        worksheet.write(len(self.shedules.all()) + 8, 2, 'Time', bold_format)
        worksheet.write(len(self.shedules.all()) + 8, 3, 'kW', bold_format)

        worksheet.write_column('D'+ str(len(self.shedules.all()) + 10), records_value)
        worksheet.write_column('B'+ str(len(self.shedules.all()) + 10), records_vlists)
        worksheet.write_column('C'+ str(len(self.shedules.all()) + 10), records_hours)


        # record_data = []
        # for i, record in enumerate(records):
        #     naive_datetime = make_naive(record.interval_start, cet)
        #     j = i + len(self.shedules.all()) + 9
        #     worksheet.write_datetime(j, 1, naive_datetime, date_format)
        #     worksheet.write_datetime(j, 2, naive_datetime, time_format)
        #     worksheet.write_number(j, 3, record.value)
        #
        # chart.add_series({
        #     'categories': '=Sheet1!$B$16:$B',
        #     'values': '=Sheet1!$D$16:$D',
        #     })
        # chart.set_x_axis({
        #     'date_axis': True,
        #     })
        #
        # # Turn off the legend.
        # chart.set_legend({'none': True})
        #
        # # Insert the chart into the worksheet.
        # worksheet.insert_chart('H23', chart)

        workbook.close()

        data_name = self.datetime_from
        data_name_to = self.datetime_to

        data = ContentFile(output.getvalue())
        self.result_file.save(
            name='{}-{}-{}_{}_{}.xlsx'.format(self.meter.site.name, 'from', self.meter.site.company, data_name.strftime("%b%d-%Y"), data_name_to.strftime("%b%d-%Y")),
            content=data,
            save=False
        )
        self.save()
