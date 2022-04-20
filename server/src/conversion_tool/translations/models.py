from django.db import models
from datetime import datetime, timedelta, time
from collections import OrderedDict
from collections import defaultdict
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils.timezone import override as override_timezone
import pytz
from pytz import country_timezones
import StringIO
import xlsxwriter
from contextlib import closing
from django.db import connection
from operator import itemgetter
from xlrd import open_workbook, xldate
import json
import io
import csv
import os
import re
from geo.models import *
from core.models import *
from companies.models import *
from core.logic.upload_data import *
from core.logic.db.upload import *
from core.logic.peak import peak_data, med_month, months, weekly, headge, cc_season, headge_calcul
from math import *   # make all math functions available
import sys
import ast



class TranslationRecord(TimeStampedModel):
    meter = models.ForeignKey('companies.Meter')
    value = models.FloatField()
    unit = models.CharField(max_length=255)
    interval_start = models.DateTimeField()
    interval = models.DurationField()
    # year = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ('-interval_start',)

    def __unicode__(self):
        return '{}: {} {}'.format(self.interval_start, self.value, self.unit)

    def get_weekday_name(self):
        return calendar.day_name[self.interval_start.weekday()]

    def get_weekday_code(self):
        return self.interval_start.toordinal() % 7 + 1


class Translation(models.Model):
    created = models.DateTimeField(default=datetime.now, blank=True)
    cc = models.ForeignKey('companies.Meter', null=True, related_name='cc_translation')
    years = models.CharField(blank=True, max_length=100)

    def __unicode__(self):
        return '{}'.format(self.created)

    class Meta:
        ordering = ('-pk',)

    def save(self, *args, **kwargs):
        super(Translation, self).save(*args, **kwargs)
        self.process_data()

    def process_data(self):
        cet = pytz.timezone('UTC')
        # cett = pytz.timezone('UTC')
        frecord = EnergyConsumptionRecord.objects.filter(meter=self.cc).order_by('interval_start')[0]
        data_year = int(frecord.interval_start.year)
        # data_year = int(datetime.now().year)-1
        td = frecord.interval
        cc_from = cet.localize(datetime(data_year, 01, 01, 0, 0), is_dst=None)
        cc_to = cet.localize(datetime(data_year, 12, 31, 23, 59), is_dst=None)
        cet_cc_from = make_aware(cc_from.replace(tzinfo=None), cet, is_dst=None)
        cet_cc_to = make_aware(cc_to.replace(tzinfo=None), cet, is_dst=None)

        all_data = EnergyConsumptionRecord.objects.filter(
            meter=self.cc,
            interval_start__gte=cet_cc_from,
            interval_start__lte=cet_cc_to
        ).order_by('interval_start')

        holidays = Holiday.objects.filter(
            country='CH',
            # date__year=data_year,
        ).values_list('date', flat=True)

        holiday_list = []
        for v in holidays:
            holiday_list.append(v.isoformat())

        holidays_meter = [] # holidays by hour (of the data that will be translated)
        
        sundays_meter = []
        sundays_octo_meter = []

        sunday_meter = []
        sunday_octo_meter = []

        data_by_day = defaultdict(list)
        for dt in all_data:
            w_cet = make_naive(dt.interval_start, cet)
            weekdend = str(w_cet)[5:16]
            if str(w_cet)[:10] in holiday_list:
                holidays_meter.append({'hour':weekdend, 'value': dt.value})
                # data_by_day[str(dt.interval_start.weekday())].append({'hour':weekdend, 'value':dt.value})
            else:
                data_by_day[str(dt.interval_start.weekday())].append({'hour':weekdend, 'value':dt.value})
            
            if str(w_cet)[5:7] == '03':
                    if w_cet.isoweekday() == 7:
                        sundays_meter.append(str(w_cet)[:10])
            
            if str(w_cet)[5:7] == '10':
                    if w_cet.isoweekday() == 7:
                        sundays_octo_meter.append(str(w_cet)[:10])
        
        # print 'data_by_day', data_by_day
        # print 'sundays_meter ============= ', sorted(sundays_meter)[-1]
        # print 'sundays_octo_meter ============= ', sorted(sundays_octo_meter)[-1]

        for dsund in data_by_day['6']:
            if dsund['hour'][:5] == sorted(sundays_meter)[-1][5:]:
                sunday_meter.append(dsund)
            if dsund['hour'][:5] == sorted(sundays_octo_meter)[-1][5:]:
                sunday_octo_meter.append(dsund)
        
        for i in range(5):
            for delete_sun in data_by_day['6']:
                if delete_sun in sunday_meter:
                    # print 'delete_sun =================== ', i,  delete_sun
                    data_by_day['6'].remove(delete_sun)
        
        # print 'sunday_octo_meter =========== ', sunday_octo_meter
        for i in range(5):
            for delete_sun in data_by_day['6']:
                if delete_sun in sunday_octo_meter:
                    # print 'delete_sun ============================== ', i,  delete_sun
                    data_by_day['6'].remove(delete_sun)

        # print 'after deleteing == ', sorted(data_by_day['6'], key=lambda k: k['hour'])


        # print 'sunday_meter ============= ', sunday_meter
        # translation_years = map(lambda xv: {'year': data_year + xv, 'value': 20}, range(1,7))
        translation_years = map(lambda xv: {'year': xv, 'value': json.loads(self.years)[xv]}, json.loads(self.years).keys())
        print 'translations', translation_years

        stream = StringIO.StringIO()
        writer = csv.writer(stream, delimiter='\t')

        for translated_year in translation_years:
            previous_years = [year for year in range(int(data_year), int(translated_year['year'])+1)]
            print 'trnaslated year = ', translated_year['year'], float(translated_year['value'])
            print 'previous_years ============ ', previous_years
            tc_from = cet.localize(datetime(int(translated_year['year']), 01, 01, 0, 0), is_dst=None)
            tc_to = cet.localize(datetime(int(translated_year['year']), 12, 31, 23, 59), is_dst=None)
            translated_holidays = Holiday.objects.filter(
                country='CH',
                # country='CH',
                # date__year=int(translated_year['year']),
            ).values_list('date', flat=True)

            translated_holiday_list = []
            for v in translated_holidays:
                translated_holiday_list.append(v.isoformat())

            # print 'holiday translated list = ', translated_holiday_list
            # print 'data ', tc_from, tc_to , td
            # tc_from = datetime(int(translated_year['year']), 01, 01, 0, 0)
            # tc_to = datetime(int(translated_year['year']), 12, 31, 23, 59)

            last = tc_to
            holiday_days = []       # weekend days by hour (of the translated year)
            next_day = tc_from
            data_translated = defaultdict(list)
            # sundays = defaultdict(list)
            sundays = []
            sundays_octob = []
            # print next_day
            while True:
                if next_day > tc_to:
                    break
                    next_day = make_naive(next_day, cet)

                if str(next_day)[:10] in translated_holiday_list:
                    holiday_days.append(str(next_day)[5:16])
                else:
                    data_translated[str(next_day.weekday())].append(str(next_day)[5:16])
                next_day += td
                # print 'translation date = ', str(next_day), str(next_day)[5:7]
                if str(next_day)[5:7] == '03':
                    if next_day.isoweekday() == 7:
                        sundays.append(str(next_day)[:10])
                
                if str(next_day)[5:7] == '10':
                    if next_day.isoweekday() == 7:
                        sundays_octob.append(str(next_day)[:10])

            # print 'data_translated == ', data_translated['6']
            # print 'sundays_octob === ', sorted(sundays_octob)[-1]
            sunday_mars = []
            sunday_octob_mars = []
            for day in data_translated['6']:
                if day[:5] == sorted(sundays)[-1][5:]:
                    sunday_mars.append(day)
                if day[:5] == sorted(sundays_octob)[-1][5:]:
                    sunday_octob_mars.append(day)


            for i in range(5):
                for del_sun in data_translated['6']:
                    if del_sun in sunday_mars:
                        # print 'data_translated every special hour delete', i,  del_sun
                        data_translated['6'].remove(del_sun)
            
            for i in range(5):
                for del_osun in data_translated['6']:
                    if del_osun in sunday_octob_mars:
                        # print 'data_translated every special hour delete', i,  del_sun
                        data_translated['6'].remove(del_osun)

            for snd in sunday_mars:
                if snd[6:] == '02:00':
                    sunday_mars.remove(snd)
            
            # for snd in sunday_octob_mars:
            #     if snd[6:] == '02:00':
            sunday_octob_mars.append(sunday_octob_mars[0][:6] + '02:00')
            # print 'sunday_octob_mars == ', sorted(sunday_octob_mars)


            # print 'sunday_mars =================== ', sunday_mars

            #
            # # Last sunday from march translation
            #

            #
            # # Percent for all previous years translation
            #
            procent_value = 1
            for pyear in sorted(previous_years):
                for tran_year in translation_years:
                    if int(pyear) == int(tran_year['year']):
                        print 'each year = ', int(pyear) == int(tran_year['year'])
                        procent_value = procent_value * (1 + float(tran_year['value'])/100)

            print 'procent value ============================== ', int(translated_year['year']), procent_value

            for i, sunday in enumerate(sunday_mars):
                if sunday[6:] == sunday_meter[i]['hour'][6:]:
                    sun_data = pytz.utc.localize(datetime(int(translated_year['year']), int(sunday[:2]), int(sunday[3:5]), 
                                                            int(sunday[6:8]), int(sunday[9:11])))
                    interval_start = sun_data.astimezone(pytz.timezone('UTC'))
                    # print 'translated sunday = ', interval_start, sunday_meter[i]['value']
                    if float(translated_year['value']) == 0:
                        writer.writerow([datetime.now(), datetime.now(), int(self.cc.id), sunday_meter[i]['value'] * procent_value, interval_start, td, 'kWh'])
                        # print 'translated sunday = ', sunday_meter[i]['value'], interval_start
                    else:
                        writer.writerow([datetime.now(), datetime.now(), int(self.cc.id), sunday_meter[i]['value'] * procent_value, interval_start, td, 'kWh'])

            #
            # # Last sunday from october translation
            #

            for i, sund in enumerate(sorted(sunday_octob_mars)):
                # print sund[6:],  sunday_octo_meter[i]['hour'][6:]
                if sund[6:] == sunday_octo_meter[i]['hour'][6:]:
                    suno_data = pytz.utc.localize(datetime(int(translated_year['year']), int(sund[:2]), int(sund[3:5]),
                                                          int(sund[6:8]), int(sund[9:11])))
                    interval_start = suno_data.astimezone(pytz.timezone('UTC'))
                    # print 'translated sunday octomber ============= ', interval_start, sunday_octo_meter[i]['value']
                    if float(translated_year['value']) == 0:
                        writer.writerow([datetime.now(), datetime.now(), int(self.cc.id), sunday_octo_meter[i]['value'] * procent_value, interval_start, td, 'kWh'])
                        # print 'translated sunday = ', sunday_octo_meter[i]['value'], interval_start
                    else:
                        writer.writerow([datetime.now(), datetime.now(), int(self.cc.id), sunday_octo_meter[i]['value'] * procent_value, interval_start, td, 'kWh'])


            #
            # # Holiday translation
            #

            hol_min = min([len(holiday_days),len(holidays_meter)])
            hol_rows = []
            for k in range(hol_min):
                # print 'holiday = ', str(translated_year['year']), holiday_days[k][:2], holiday_days[k][3:5], holiday_days[k][6:8], holiday_days[k][9:11], holiday_days[k]
                hol_data = pytz.utc.localize(datetime(int(translated_year['year']), int(holiday_days[k][:2]), int(holiday_days[k][3:5]), int(holiday_days[k][6:8]), int(holiday_days[k][9:11])))
                interval_start = hol_data.astimezone(pytz.timezone('UTC'))
                # print 'holiday value = ', ([datetime.now(), datetime.now(), int(self.cc.id), holidays_meter[k]['value'], interval_start, td, 'kWh'])
                if float(translated_year['value']) == 0:
                    writer.writerow([datetime.now(), datetime.now(), int(self.cc.id), holidays_meter[k]['value'] * procent_value, interval_start, td, 'kWh'])
                else:
                    writer.writerow([datetime.now(), datetime.now(), int(self.cc.id), holidays_meter[k]['value'] * procent_value, interval_start, td, 'kWh'])
            #
            # # All remained days translation
            #

            data_rows = []
            for key in data_by_day.keys():
                min_val = min(len(data_by_day[key]), len(data_translated[key]))
                if min_val == len(data_translated[key]):
                    for index in range(min_val):
                        # print 'key min_val == len(data_translated[key]) == ', key, str(translated_year['year']) + ' ' + data_translated[key][index], data_by_day[key][index]['value'], (len(data_translated[key]) - len(data_by_day[key]))
                        hol_data = pytz.utc.localize(datetime(int(translated_year['year']), int(data_translated[key][index][:2]), int(data_translated[key][index][3:5]), int(data_translated[key][index][6:8]), int(data_translated[key][index][9:11])))
                        interval_start = hol_data.astimezone(pytz.timezone('UTC'))
                        if float(translated_year['value']) == 0:
                            writer.writerow([datetime.now(), datetime.now(), int(self.cc.id), data_by_day[key][index]['value'] * procent_value, interval_start, td, 'kWh'])
                        else:
                            writer.writerow([datetime.now(), datetime.now(), int(self.cc.id), data_by_day[key][index]['value'] * procent_value, interval_start, td, 'kWh'])
                elif min_val == len(data_by_day[key]):
                    # print data_translated[key][0] , data_by_day[key][0]['hour'], len(data_translated[key]) , len(data_by_day[key]), len(data_translated[key]) - len(data_by_day[key])
                    data_by_day[key] = data_by_day[key] + data_by_day[key][-(len(data_translated[key]) - len(data_by_day[key])):]
                    for index in range(len(data_by_day[key])):
                        # print 'key min_val == len(data_by_day[key]) == ', key, str(translated_year['year']) + ' ' + data_translated[key][index], data_by_day[key][index]['value'], (len(data_translated[key]) - len(data_by_day[key]))
                        hol_data = pytz.utc.localize(datetime(int(translated_year['year']), int(data_translated[key][index][:2]), int(data_translated[key][index][3:5]), int(data_translated[key][index][6:8]), int(data_translated[key][index][9:11])))
                        interval_start = hol_data.astimezone(pytz.timezone('UTC'))
                        if float(translated_year['value']) == 0:
                            writer.writerow([datetime.now(), datetime.now(), int(self.cc.id), data_by_day[key][index]['value'] * procent_value, interval_start, td, 'kWh'])
                        else:
                            writer.writerow([datetime.now(), datetime.now(), int(self.cc.id), data_by_day[key][index]['value'] * procent_value, interval_start, td, 'kWh'])

        stream.seek(0)
        with closing(connection.cursor()) as cursor:
            cursor.copy_from(
                file=stream,
                table='translations_translationrecord',
                sep='\t',
                columns=('created', 'modified', 'meter_id', 'value', 'interval_start', 'interval', 'unit'),
            )


    def upload_meter(self):
        print 'upload_meter'
        cet = pytz.timezone('UTC')
        cett = pytz.timezone('CET')
        years = []
        # data_year = int(datetime.now().year)-1
        transaction_years = map(lambda year: int(year), json.loads(self.years).keys())
        years = transaction_years + [int(self.cc.site.year)]
        # years = json.loads(self.years).keys()
        years = sorted(years)
        print 'years == ', years
        for year in years:
            cc_from = cet.localize(datetime(year, 01, 01, 0, 0), is_dst=None)
            cc_to = cet.localize(datetime(year, 12, 31, 23, 59), is_dst=None)
            if year in transaction_years:
                data_list = TranslationRecord.objects.filter(meter = self.cc,
                                                           interval_start__gte=cc_from,
                                                           interval_start__lte=cc_to
                                                           ).values('interval_start', 'value')
            else :
                data_list = EnergyConsumptionRecord.objects.filter(meter = self.cc,
                                                                 interval_start__gte=cc_from,
                                                                 interval_start__lte=cc_to
                                                                 ).values('interval_start', 'value')
            months_all = [str(dt)[:7] for dt in rrule(MONTHLY, dtstart=cc_from, until=cc_to)]
            # print 'months = ', months_all
            sheet_col = {}
            for i, month in enumerate(months_all):
                sheet_col[month] = 3 +  i
            peak_list = []
            headge_list = []
            total = []
            total_max = []
            shedules = Shedule.objects.filter(id__in=[1,2])
            # print shedules
            rec_list = []
            # print 'all data_list == ', year, data_list
            headges_med = {}
            print('length of hours = ', len(data_list))
            for index, shedule in enumerate(shedules):
                peak_list, headge_list = peak_data(self, shedule, data_list)
                # print 'headge_list = ', headge_list
                peak_month, peak_month_list = med_month(peak_list, shedule)
                total, total_max = months(self, year, sheet_col, index, shedule, months_all, peak_month)
                cc_season(self, year, peak_list, shedule)
                headge_calcul(self, shedule, year, data_list)
                # headges_med = headge(self, headge_list, shedule, year)
                # print 'peak list == ', headge_list
                # print 'peak list == ', peak_list
            
            sum_year =  sum(item['value'] for item in data_list) / len(data_list)
            for data in data_list:
                weekd_cet = make_naive(data['interval_start'], cet)
                rec_list.append({weekd_cet: data['value']})
                # print 'headges === ', weekd_cet.year, data['value'], ' sum year == ', sum_year, ' med per peak = ', headges_med[str(weekd_cet.year)]
            
            weekly(self, rec_list, year)

