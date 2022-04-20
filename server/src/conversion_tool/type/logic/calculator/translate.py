# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division
from datetime import datetime, timedelta, time
import calendar
from collections import OrderedDict
from collections import defaultdict
from django.dispatch import receiver
from django.db.models.signals import post_save
from dateutil.rrule import rrule, MONTHLY
from django.db import models, connection
import pytz
import os
from operator import itemgetter
from xlrd import open_workbook, xldate
import xlsxwriter
import StringIO
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from geo.models import *
from core.models import *
from django.db import transaction
from itertools import groupby


def to_date(date):
    return datetime.strptime(str(date)[:16], '%Y-%m-%d %H:%M')

class Translation():
    worksheet = None

    def __init__(self, all_data, year, years_value, worksheet):
        data_year = year        
        cet = pytz.timezone('UTC')
        td = timedelta(hours=1)

        holidays = Holiday.objects.filter(
            country='CH',
        ).values_list('date', flat=True)

        holiday_list = []
        for v in holidays:
            holiday_list.append(v.isoformat())

        holidays_meter = []  # holidays by hour (of the data that will be translated)
        sundays_meter = []
        sundays_octo_meter = []
        sunday_meter = []
        sunday_octo_meter = []

        data_by_day = defaultdict(list)
        for dt in all_data:
            # w_cet = make_naive(dt['interval_start'], cet)
            w_cet = dt['interval_start']
            weekdend = str(w_cet)[5:16]
            if str(w_cet)[:10] in holiday_list:
                holidays_meter.append({'hour': weekdend, 'value': dt['value']})
                # data_by_day[str(dt.interval_start.weekday())].append({'hour':weekdend, 'value':dt['value']})
            else:
                data_by_day[str(dt['interval_start'].weekday())].append({'hour': weekdend, 'value': dt['value']})

            if str(w_cet)[5:7] == '03':
                    if w_cet.isoweekday() == 7:
                        sundays_meter.append(str(w_cet)[:10])

            if str(w_cet)[5:7] == '10':
                    if w_cet.isoweekday() == 7:
                        sundays_octo_meter.append(str(w_cet)[:10])

        # print 'data_by_day', data_by_day
        print 'sundays_meter ============= ', sorted(sundays_meter)[-1]
        print 'sundays_octo_meter ============= ', sorted(sundays_octo_meter)[-1]

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

        years_value = years_value.split(',')
        
        years = [int(data_year) + nr + 1 for nr in range(len(years_value))]
        translation_years = []
        for i, year in enumerate(years):
            translation_years.append({'year': year, 'value': int(years_value[i])})
        
        # translation_years = map(lambda xv: {'year': xv, 'value': years_value)[xv]}, years)
        #     print 'translations', translation_years

        for col, translated_year in enumerate(translation_years):
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

            print 'holiday translated list = ', translated_holiday_list
            # print 'data ', tc_from, tc_to , td
            # tc_from = datetime(int(translated_year['year']), 01, 01, 0, 0)
            # tc_to = datetime(int(translated_year['year']), 12, 31, 23, 59)

            last = tc_to
            holiday_days = []       # weekend days by hour (of the translated year)
            next_day = tc_from
            data_translated = defaultdict(list)
            sundays = []
            sundays_octob = []

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
            print 'sundays_octob === ', sorted(sundays_octob)[-1]
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
                        print(sunday_meter[i]['value'] * procent_value, interval_start, col+1)
                        worksheet.write(i+1, col+1, interval_start.replace(tzinfo=None))
                        worksheet.write(i+1, col+1, sunday_meter[i]['value'] * procent_value)
                        # print 'translated sunday = ', sunday_meter[i]['value'], interval_start
                    else:
                        print(sunday_meter[i]['value'] * procent_value, interval_start, col+1)
                        worksheet.write(i+1, col+1, interval_start.replace(tzinfo=None))
                        worksheet.write(i+1, col+1, sunday_meter[i]['value'] * procent_value)

            #
            # # Last sunday from october translation
            #
            try:
                for i, sund in enumerate(sorted(sunday_octob_mars)):
                    print sund[6:],  sunday_octo_meter[i]['hour'][6:]
                    if sund[6:] == sunday_octo_meter[i]['hour'][6:]:
                        suno_data = pytz.utc.localize(datetime(int(translated_year['year']), int(sund[:2]), int(sund[3:5]), int(sund[6:8]), int(sund[9:11])))
                        interval_start = suno_data.astimezone(pytz.timezone('UTC'))
                        # print 'translated sunday octomber ============= ', interval_start, sunday_octo_meter[i]['value']
                        if float(translated_year['value']) == 0:
                            print(sunday_octo_meter[i]['value'] * procent_value, interval_start, col+1)
                            # print 'translated sunday = ', sunday_octo_meter[i]['value'], interval_start
                            worksheet.write(i+1, col+1, interval_start.replace(tzinfo=None))
                            worksheet.write(i+1, col+1, sunday_octo_meter[i]['value'] * procent_value)
                        else:
                            print(sunday_octo_meter[i]['value'] * procent_value, interval_start, col+1)
                            worksheet.write(i+1, col+1, interval_start.replace(tzinfo=None))
                            worksheet.write(i+1, col+1, sunday_octo_meter[i]['value'] * procent_value)
            except:
                pass
            #
            # # Holiday translation
            #

            hol_min = min([len(holiday_days), len(holidays_meter)])
            hol_rows = []
            for k in range(hol_min):
                # print 'holiday = ', str(translated_year['year']), holiday_days[k][:2], holiday_days[k][3:5], holiday_days[k][6:8], holiday_days[k][9:11], holiday_days[k]
                hol_data = pytz.utc.localize(datetime(int(translated_year['year']), int(holiday_days[k][:2]), int(
                    holiday_days[k][3:5]), int(holiday_days[k][6:8]), int(holiday_days[k][9:11])))
                interval_start = hol_data.astimezone(pytz.timezone('UTC'))
                # print 'holiday value = ', ([holidays_meter[k]['value'], interval_start])
                if float(translated_year['value']) == 0:
                    print(holidays_meter[k]['value'] * procent_value, interval_start, col+1)
                    worksheet.write(i+1, col+1, interval_start.replace(tzinfo=None))
                    worksheet.write(i+1, col+1, holidays_meter[i]['value'] * procent_value)
                else:
                    print(holidays_meter[k]['value'] * procent_value, interval_start, col+1)
                    worksheet.write(i+1, col+1, interval_start.replace(tzinfo=None))
                    worksheet.write(i+1, col+1, holidays_meter[i]['value'] * procent_value)
            #
            # # All remained days translation
            #

            data_rows = []
            for key in data_by_day.keys():
                min_val = min(len(data_by_day[key]), len(data_translated[key]))
                if min_val == len(data_translated[key]):
                    for index in range(min_val):
                        # print 'key min_val == len(data_translated[key]) == ', key, str(translated_year['year']) + ' ' + data_translated[key][index], data_by_day[key][index]['value'], (len(data_translated[key]) - len(data_by_day[key]))
                        hol_data = pytz.utc.localize(datetime(int(translated_year['year']), int(data_translated[key][index][:2]), int(
                            data_translated[key][index][3:5]), int(data_translated[key][index][6:8]), int(data_translated[key][index][9:11])))
                        interval_start = hol_data.astimezone(pytz.timezone('UTC'))
                        if float(translated_year['value']) == 0:
                            print(data_by_day[key][index]['value'] * procent_value, interval_start, col+1)
                            worksheet.write(i+1, col+1, interval_start.replace(tzinfo=None))
                            worksheet.write(i+1, col+1, data_by_day[key][index]['value'] * procent_value)
                        else:
                            print(data_by_day[key][index]['value'] * procent_value, interval_start, col+1)
                            worksheet.write(i+1, col+1, interval_start.replace(tzinfo=None))
                            worksheet.write(i+1, col+1, data_by_day[key][index]['value'] * procent_value)
                elif min_val == len(data_by_day[key]):
                    # print data_translated[key][0] , data_by_day[key][0]['hour'], len(data_translated[key]) , len(data_by_day[key]), len(data_translated[key]) - len(data_by_day[key])
                    data_by_day[key] = data_by_day[key] + \
                        data_by_day[key][-(len(data_translated[key]) - len(data_by_day[key])):]
                    for index in range(len(data_by_day[key])):
                        # print 'key min_val == len(data_by_day[key]) == ', key, str(translated_year['year']) + ' ' + data_translated[key][index], data_by_day[key][index]['value'], (len(data_translated[key]) - len(data_by_day[key]))
                        hol_data = pytz.utc.localize(datetime(int(translated_year['year']), int(data_translated[key][index][:2]), int(
                            data_translated[key][index][3:5]), int(data_translated[key][index][6:8]), int(data_translated[key][index][9:11])))
                        interval_start = hol_data.astimezone(pytz.timezone('UTC'))
                        if float(translated_year['value']) == 0:
                            print(data_by_day[key][index]['value'] * procent_value, interval_start, col+1)
                            worksheet.write(i+1, col+1, interval_start.replace(tzinfo=None))
                            worksheet.write(i+1, col+1, data_by_day[key][index]['value'] * procent_value)
                        else:
                            print(data_by_day[key][index]['value'] * procent_value, interval_start, col+1)
                            worksheet.write(i+1, col+1, interval_start.replace(tzinfo=None))
                            worksheet.write(i+1, col+1, data_by_day[key][index]['value'] * procent_value)
        self.worksheet = worksheet
