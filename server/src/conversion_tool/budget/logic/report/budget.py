import calendar
from datetime import datetime, timedelta, time
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils.timezone import override as override_timezone
import pytz
from pytz import country_timezones


def peak_data(self, shedule, budget_data):
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

    peak_list = []
    headge_list = []
    for data in budget_data:
        data_cet = make_naive(data['interval_start'], cet)
        weekday = int(datetime.strptime(str(data_cet)[:10], '%Y-%m-%d').isoweekday())
        hours = int(str(data_cet)[11:13])
        hour = time(int(str(data_cet)[11:13]), int(str(data_cet)[14:16]))
        day = str(data_cet)[:10]
        month_dic = str(data_cet)[:7]
        month = int(str(data_cet)[5:7])

        if ((hours in hourss) and (month in months) and (weekday in weekdays) and ((day not in holiday_list) == True)):
            peak_list.append({month_dic: data['value']})
            headge_list.append({weekday: data['value']})
            # print 'Simple day = ', shedule.title, data_cet, month_dic

        if ((day in holiday_list) == True) and (shedule.holiday == True):
            if ((hours in hourss) and (month in months) and (weekday in weekdays)):
                peak_list.append({month_dic: data['value']})
                headge_list.append({weekday: data['value']})
                # print 'Holiday with first checkbox = ', shedule.title, data_cet, month_dic

        if ((weekday in weekend_days) and (month in months) and ((day in holiday_list) == True) and (shedule.weekend == True) and (shedule.holiday == True)):
            peak_list.append({month_dic: data['value']})
            headge_list.append({weekday: data['value']})
            # print 'Holiday as normal coincide cu weekend = ', shedule.title, data_cet

        if (((day in holiday_list) == True) and (month in months) and (shedule.all_holidays == True)):
            peak_list.append({month_dic: data['value']})
            headge_list.append({weekday: data['value']})
            # print shedule.title, shedule.all_holidays, 'All holidays ========== ', data['interval_start']

        if ((weekday in weekend_days) and (month in months) and ((day not in holiday_list) == True) and (shedule.weekend == True)):
            peak_list.append({month_dic: data['value']})
            headge_list.append({weekday: data['value']})
            # print shedule.title, shedule.weekend, 'All weekend data ========== ', data['interval_start']

    return peak_list, headge_list


def cc_data(self, shedule, cc_med_data):
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

    peak_list = []
    for data in cc_med_data:
        data_cet = make_naive(data['interval_start'], cet)
        weekday = int(datetime.strptime(str(data_cet)[:10], '%Y-%m-%d').isoweekday())
        hours = int(str(data_cet)[11:13])
        hour = time(int(str(data_cet)[11:13]), int(str(data_cet)[14:16]))
        day = str(data_cet)[:10]
        month_dic = str(data_cet)[:7]
        month = int(str(data_cet)[5:7])

        if ((hours in hourss) and (month in months) and (weekday in weekdays) and ((day not in holiday_list) == True)):
            peak_list.append({month_dic: data['value']})
            # print 'Simple day = ', shedule.title, data_cet, month_dic

        if ((day in holiday_list) == True) and (shedule.holiday == True):
            if ((hours in hourss) and (month in months) and (weekday in weekdays)):
                peak_list.append({month_dic: data['value']})
                # print 'Holiday with first checkbox = ', shedule.title, data_cet, month_dic

        if ((weekday in weekend_days) and (month in months) and ((day in holiday_list) == True) and (shedule.weekend == True) and (shedule.holiday == True)):
            peak_list.append({month_dic: data['value']})
            # print 'Holiday as normal coincide cu weekend = ', shedule.title, data_cet

        if (((day in holiday_list) == True) and (month in months) and (shedule.all_holidays == True)):
            peak_list.append({month_dic: data['value']})
            # print shedule.title, shedule.all_holidays, 'All holidays ========== ', data['interval_start']

        if ((weekday in weekend_days) and (month in months) and ((day not in holiday_list) == True) and (shedule.weekend == True)):
            peak_list.append({month_dic: data['value']})
            # print shedule.title, shedule.weekend, 'All weekend data ========== ', data['interval_start']

    return peak_list
