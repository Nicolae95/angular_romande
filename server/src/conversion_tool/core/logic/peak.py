import calendar
from datetime import datetime, timedelta, time
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils.timezone import override as override_timezone
import pytz
from pytz import country_timezones
from .db.upload import *
from collections import defaultdict
from operator import itemgetter
import StringIO
import xlsxwriter
import csv
import pytz
import sys
import ast
# from ..models import *
from django.apps import apps


def peak_data(self, shedule, list_data):
    cet = pytz.timezone('UTC')
    hourss = shedule.hours.all().values_list('value', flat=True)
    months = shedule.months.all().values_list('month', flat=True)
    weekdays = shedule.weekdays.all().values_list('day', flat=True)
    weekend_days = shedule.weekend_days.all().values_list('day', flat=True)
    hol = shedule.country.holidays.all().values_list('date', flat=True)
    holiday_list = []
    for v in hol:
        h = str(v)[:4]
        holiday_list.append(v.isoformat())
    print 'holiday_list == ', holiday_list
    peak_list = []
    headge_list = []
    for data in list_data:
        data_cet = make_naive(data['interval_start'], cet)
        weekday = int(datetime.strptime(str(data_cet)[:10], '%Y-%m-%d').isoweekday())
        hours = int(str(data_cet)[11:13])
        hour = time(int(str(data_cet)[11:13]), int(str(data_cet)[14:16]))
        day = str(data_cet)[:10]
        month_dic = str(data_cet)[:7]
        month = int(str(data_cet)[5:7])
        # print shedule.title, data_cet, data['value']

        if ((hours in hourss) and (month in months) and (weekday in weekdays) and ((day not in holiday_list) == True)):
            peak_list.append({month_dic: data['value']})
            headge_list.append({'weekday':weekday, 'value': data['value']})
            # print 'Simple day = ', shedule.title, data_cet, month_dic, data['value']

        if ((day in holiday_list) == True) and (shedule.holiday == True):
            if ((hours in hourss) and (month in months) and (weekday in weekdays)):
                peak_list.append({month_dic: data['value']})
                headge_list.append({'weekday': weekday, 'value': data['value']})
                # print 'Holiday with first checkbox = ', shedule.title, data_cet, month_dic, data['value']

        if ((weekday in weekend_days) and (month in months) and ((day in holiday_list) == True) and (shedule.weekend == True) and (shedule.holiday == True)):
            peak_list.append({month_dic: data['value']})
            headge_list.append({'weekday':weekday, 'value': data['value']})
            # print 'Holiday as normal coincide cu weekend = ', shedule.title, data_cet, month_dic, data['value']

        if (((day in holiday_list) == True) and (month in months) and (shedule.all_holidays == True)):
            peak_list.append({month_dic: data['value']})
            headge_list.append({'weekday':weekday, 'value': data['value']})
            # print shedule.title, shedule.all_holidays, 'All holidays ========== ', data_cet, month_dic, data['value']

        if ((weekday in weekend_days) and (month in months) and ((day not in holiday_list) == True) and (shedule.weekend == True)):
            peak_list.append({month_dic: data['value']})
            headge_list.append({'weekday':weekday, 'value': data['value']})
            # print shedule.title, shedule.weekend, 'All weekend data ========== ', data_cet, month_dic, data['value']

    # print peak_list
    return peak_list, headge_list


def med_month(peak_list, shedule):
    peak_data_list = defaultdict(list)
    peak_data_res = []
    for d in peak_list: # you can list as many input dicts as you want here
        for key, value in d.iteritems():
            peak_data_list[key].append(value)
    for key in peak_data_list.keys():
        # print({'month':key, 'max' : max(item for item in peak_data_list[key]), 'value' : sum(item for item in peak_data_list[key])/ len(peak_data_list[key])-1 })
        peak_data_res.append({'month':key, 'max' : max(item for item in peak_data_list[key]), 'lenght': len(peak_data_list[key])-1, 'value' : sum(item for item in peak_data_list[key])})
    peak_data_res = sorted(peak_data_res, key=itemgetter('month'))
    return peak_data_res , peak_data_list

def months(self, year, sheet_col, index, shedule, months_all, peak_data_res):
    cet = pytz.timezone('UTC')
    streamw = StringIO.StringIO()
    writer = csv.writer(streamw, delimiter='\t')
    total = []
    total_max = []
    total_peak = 0
    for p, value in enumerate(peak_data_res):
        total_peak += value['value']
        total.append({value['month']: value['value']})
        total_max.append({value['month']: value['max']})
        # print 'value = ', value['month'], datetime.strptime(value['month'], '%Y-%m').month, value['value'], year, self.cc.id
        writer.writerow([datetime.now(), self.cc.id, int(shedule.id), int(year), int(datetime.strptime(value['month'], '%Y-%m').month), value['value'], 'kWh'])
    upload_month(streamw)
    return total, total_max

def cc_season(self, year, cc_data_list, shedule):
    streamw = StringIO.StringIO()
    writer = csv.writer(streamw, delimiter='\t')
    cc_data_med_res = defaultdict(list)
    cc_data_res = defaultdict(list)
    cc_data_res_shedule = []
    for d in cc_data_list: # you can list as many input dicts as you want here
        for key, value in d.iteritems():
            cc_data_res[key].append(value)
    for key in cc_data_res.keys():
        # cc_data_res_shedule += cc_data_res[key]
        month_med = datetime.strptime(key,'%Y-%m').month
        if month_med in [4,5,6,7,8,9]:
            cc_data_med_res['summer'] += cc_data_res[key]
        else :
            cc_data_med_res['winter'] += cc_data_res[key]
    # print 'cc data med summer === ', float(sum(item for item in cc_data_med_res['summer']))
    # print 'cc data med winter === ', float(sum(item for item in cc_data_med_res['winter']))
    writer.writerow([datetime.now(), self.cc.id, shedule.id, year, 'Summer', float(sum(item for item in cc_data_med_res['summer'])), 'kWh'])
    writer.writerow([datetime.now(), self.cc.id, shedule.id, year, 'Winter', float(sum(item for item in cc_data_med_res['winter'])), 'kWh'])
    upload_sea(streamw)
    # return cc_data_med_res

def weekly(self, rec_list, year_date):
    cet = pytz.timezone('UTC')
    streamw = StringIO.StringIO()
    writer = csv.writer(streamw, delimiter='\t')
    peak_data_rec_list = defaultdict(list)
    weekly = []
    for d in rec_list: # you can list as many input dicts as you want here
        for key, value in d.iteritems():
            peak_data_rec_list[key].append(value)

    for key in peak_data_rec_list.keys():
        # data_cet = make_naive(key, cet)
        # weekday = int(datetime.strptime(data_cet[:10], '%Y-%m-%d').isoweekday())
        weekday = int(datetime.strptime(str(key)[:10], '%Y-%m-%d').isoweekday())
        hour = int(str(key)[11:13])
        # print 'weeeeekly day = ', key, 'weekday = ', weekday ,', hour = ', hour
        weekly.append({(weekday-1)*24+hour: sum(item for item in peak_data_rec_list[key])})
    #
    # Media data by weekly hour
    #
    weekly_list = defaultdict(list)
    weekly_res = []
    for d in weekly: # you can list as many input dicts as you want here
        for key, value in d.iteritems():
            weekly_list[key].append(value)
    for key in weekly_list.keys():
        weekly_res.append({'hour':key, 'value' : sum(item for item in weekly_list[key])/ len(weekly_list[key])})
        # print({'hour':key, 'value' : sum(item for item in weekly_list[key])/ len(weekly_list[key])})
        writer.writerow([datetime.now(), int(self.cc.id), int(year_date), int(key), (sum(item for item in weekly_list[key])/ float(len(weekly_list[key]))), 'kWh'])
    upload_weekly(streamw)


def headge(self, headge_list, shedule, year_date):
    shedules = defaultdict()
    if shedule.weekend == False:
        shedules[str(year_date)] = sum(item['value'] for item in headge_list) / len(headge_list)
    else:
        shedules[str(year_date)] = 0
    return shedules


def headge_calcul(self, shedule, year, data_list):
    # HeadgeRecord
    streamh = StringIO.StringIO()
    writer = csv.writer(streamh, delimiter='\t')
    HeadgeRecord = apps.get_model("core", "HeadgeRecord")
    from scipy import optimize
    from sympy import symbols, Function, diff, solve
    x, y = symbols('x y')
    fs = ''
    hours = shedule.hours.all().values_list('value', flat=True)
    weekdays = shedule.weekdays.all().values_list('day', flat=True)
    weekend_days = shedule.weekend_days.all().values_list('day', flat=True)

    for cc_data in data_list:
        if ((int(cc_data['interval_start'].hour) in hours) and (int(cc_data['interval_start'].isoweekday()) in weekdays)):
            fs += 'abs(' + str(cc_data['value']) + '-x' + ')+'

        if shedule.weekend:
            if (int(cc_data['interval_start'].isoweekday()) in weekend_days):
                fs += 'abs(' + str(cc_data['value']) + '-x' + ')+'

    # print 'optimize ========================='

    def f(x):
        return eval(fs[:-1])
    # print f, type(f)
    result = optimize.minimize_scalar(f)
    # print 'headges =', result.x
    # hg = HeadgeRecord(value=float(result.x), unit='kWh', meter=self.cc, schedule=shedule, year=self.year)
    # hg.save()
    writer.writerow([datetime.now(), int(self.cc.id), int(
        shedule.id), int(year), float(result.x), 'kWh'])
    upload_head(streamh)


# def headge_calcul(self, shedule, year, data_list):
#     # HeadgeRecord
#     streamh = StringIO.StringIO()
#     writer = csv.writer(streamh, delimiter='\t')
#     HeadgeRecord = apps.get_model("core", "HeadgeRecord")
#     from scipy import optimize
#     from sympy import symbols, Function, diff, solve
#     x, y = symbols('x y')
#     fs = ''
#     hours = shedule.hours.all().values_list('value', flat=True)
#     weekdays = shedule.weekdays.all().values_list('day', flat=True)
#     weekend_days = shedule.weekend_days.all().values_list('day', flat=True)
#     hol = shedule.country.holidays.all().values_list('date', flat=True)
#     holiday_list = []
#     for v in hol:
#         h = str(v)[:4]
#         holiday_list.append(v.isoformat())
#     # print 'holiday_list optimize == ', holiday_list

#     for cc_data in data_list:
#         hdata = str(cc_data['interval_start'].isoformat())[:10]
#         # print 'hdata ==== ', hdata
#         if ((int(cc_data['interval_start'].hour) in hours) and (int(cc_data['interval_start'].isoweekday()) in weekdays) and ((hdata not in holiday_list) == True)):
#             fs += 'abs(' + str(cc_data['value']) + '-x' + ')+'
        
#         if shedule.weekend:
#             if (int(cc_data['interval_start'].isoweekday()) in weekend_days):
#                 fs += 'abs(' + str(cc_data['value']) + '-x' + ')+'
        
#         if shedule.weekend:
#             if (hdata in holiday_list):
#                 # print 'cc value holiday headges -- ', cc_data['value']
#                 fs += 'abs(' + str(cc_data['value']) + '-x' + ')+'

#     print 'optimize ========================='
#     def f(x):
#         return eval(fs[:-1])
#     # print f, type(f)
#     result = optimize.minimize_scalar(f)
#     print 'headges =', result.x
#     # hg = HeadgeRecord(value=float(result.x), unit='kWh', meter=self.cc, schedule=shedule, year=self.year)
#     # hg.save()
#     writer.writerow([datetime.now(), int(self.cc.id), int(shedule.id), int(year), float(result.x), 'kWh'])
#     upload_head(streamh)

