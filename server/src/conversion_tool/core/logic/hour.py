from datetime import datetime, timedelta, time
from django.db.models import Q, Func, Sum, Max, Count
import StringIO
import xlsxwriter
from contextlib import closing
from django.db import connection
from xlrd import open_workbook, xldate
from companies.models import Meter
import csv
import pytz
from pytz import country_timezones
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils.timezone import override as override_timezone
from collections import defaultdict
from operator import itemgetter
from db.upload import upload_db


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


def to_datetime(xldate):
    # temp = datetime(1900, 1, 1)
    temp = datetime(1899, 12, 30)
    delta = timedelta(days=xldate)
    return temp + delta + timedelta(minutes=1)


def hour_data(sheet, id, site, meters, meter_sum):
    print 'hour', sheet.ncols-1, len(meters), site.year
    stream = StringIO.StringIO()
    writer = csv.writer(stream, delimiter='\t')
    data_meters = defaultdict(list)
    data_octb_meters = defaultdict(list)
    for row in range(1, sheet.nrows):
        for col in range(1, sheet.ncols):
            if str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[5:14] + '00' == get_oct_sunday(site.year) + ' 02:00':
                print 'value last oct = ', str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[
                    5:14] + '00', sheet.cell(row, col).value
                data_octb_meters[str(col)].append({'hour': str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:10] + ' '
                                                   + str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[11:14] + '00', 'value': sheet.cell(row, col).value})
            else:
                data_meters[str(col)].append({str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:10] + ' '
                                              + str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[11:14] + '00': sheet.cell(row, col).value})

    # print 'data_octb_meters == ', data_octb_meters
    file_meters = []
    if sheet.ncols-1 == len(meters)+1:
        file_meters = sorted(list(enumerate(data_meters)), key=lambda x: x[1])[:-1]
    elif sheet.ncols-1 == len(meters):
        file_meters = sorted(list(enumerate(data_meters)), key=lambda x: x[1])
    else:
        file_meters = []

    # print 'file_meters = ', file_meters
    print 'meters ==== ', meters

    peak_list = []
    weekly_list = []
    # data_sum = defaultdict(list)
    for index, meter in sorted(file_meters, key=lambda x: x[0]):
        data_hour = defaultdict(list)
        for di in data_meters[meter]:
            for k, value in di.iteritems():
                data_hour[k].append(value)
        for key in data_hour.keys():
            interval_cc = datetime.strptime(str(key)[:16], '%Y-%m-%d %H:%M')
            print {'meter': meter, 'value': sum(
                item for item in data_hour[key]), 'interval_start': key}
            # data_sum[key].append(sum(item for item in data_hour[key]))
            writer.writerow([datetime.now(), datetime.now(), int(id), meters[index-1],
                             sum(item for item in data_hour[key]), key, timedelta(hours=1), 'kWh'])

        # print 'data_octb_meters[meter] ==== ', data_octb_meters[meter], len(data_octb_meters[meter])
        if len(data_octb_meters[meter]) == 8:
            interval_cc = datetime.strptime(
                str(data_octb_meters[meter][0]['hour'])[:16], '%Y-%m-%d %H:%M')
            # print 'lun 8 = ', interval_cc, sum(item['value'] for item in data_octb_meters[meter][:4])
            # print 'lun 8 = ', interval_cc, sum(item['value'] for item in data_octb_meters[meter][4:])
            writer.writerow([datetime.now(), datetime.now(), int(id), meters[index-1],
                             sum(item['value'] for item in data_octb_meters[meter][:4]), interval_cc, timedelta(hours=1), 'kWh'])

            writer.writerow([datetime.now(), datetime.now(), int(id), meters[index-1],
                             sum(item['value'] for item in data_octb_meters[meter][4:]), interval_cc, timedelta(hours=1), 'kWh'])

        if len(data_octb_meters[meter]) == 4:
            interval_cc = datetime.strptime(
                str(data_octb_meters[meter][0]['hour'])[:16], '%Y-%m-%d %H:%M')
            writer.writerow([datetime.now(), datetime.now(), int(id), meters[index-1],
                             sum(item['value'] for item in data_octb_meters[meter]), interval_cc, timedelta(hours=1), 'kWh'])

    upload_db(stream)


def hour_data_unic(self, sheet, hid, site, meters):
    print 'hour unic ', self.id, sheet.ncols-5, len(meters), site.year
    stream = StringIO.StringIO()
    writer = csv.writer(stream, delimiter='\t')
    # data_meters = defaultdict(list)
    data_meters = []
    data_oct_meters = []
    for row in range(1, sheet.nrows):
        hour = str(to_datetime(sheet.cell(row, 0).value))[:14] + '00'
        # print 'hour value  === ', hour, xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0), sheet.cell(row, 0).value, sheet.cell(row, 1).value
        if hour[5:] == get_oct_sunday(site.year) + ' 02:00':
            print({'hour': hour, 'value': sheet.cell(row, 1).value})
            data_oct_meters.append({'hour': hour, 'value': sheet.cell(row, 1).value})
        else:
            data_meters.append({hour: sheet.cell(row, 1).value})

    # print 'meter = ', meters[0], data_meters
    print 'meter octomber = ', data_oct_meters[:4], sum(
        item['value'] for item in data_oct_meters[:4])
    print 'second = ',  data_oct_meters[4:], sum(item['value'] for item in data_oct_meters[4:])
    print data_oct_meters
    peak_list = []
    weekly_list = []
    data_hour = defaultdict(list)
    for meter in data_meters:
        for k, value in meter.iteritems():
            data_hour[k].append(value)
    for key in data_hour.keys():
        # print {'meter':meters[0].id, 'value' : sum(item for item in data_hour[key]), 'interval_start' : key}, data_hour[key]
        interval_cc = datetime.strptime(str(key)[:16], '%Y-%m-%d %H:%M')
        writer.writerow([datetime.now(), datetime.now(), int(self.id), meters[0].id, sum(
            item for item in data_hour[key]), interval_cc, timedelta(hours=1), 'kWh'])
        peak_list.append({'interval_start': interval_cc,
                          'value': sum(item for item in data_hour[key])})
        weekly_list.append({key: sum(item for item in data_hour[key])})

    if len(data_oct_meters) == 8:
        interval_cc = datetime.strptime(str(data_oct_meters[0]['hour'])[:16], '%Y-%m-%d %H:%M')
        print 'ora 02 00 ================================================== ', interval_cc, sum(
            item['value'] for item in data_oct_meters[:4])
        writer.writerow([datetime.now(), datetime.now(), int(self.id), meters[0].id, sum(
            item['value'] for item in data_oct_meters[:4]), interval_cc, timedelta(hours=1), 'kWh'])
        peak_list.append({'interval_start': interval_cc, 'value': sum(
            item['value'] for item in data_oct_meters[:4])})
        weekly_list.append({data_oct_meters[0]['hour']: sum(
            item['value'] for item in data_oct_meters[:4])})
        writer.writerow([datetime.now(), datetime.now(), int(self.id), meters[0].id, sum(
            item['value'] for item in data_oct_meters[4:]), interval_cc, timedelta(hours=1), 'kWh'])
        peak_list.append({'interval_start': interval_cc, 'value': sum(
            item['value'] for item in data_oct_meters[4:])})
        print 'ora 02 00 ================================================== ', interval_cc, sum(
            item['value'] for item in data_oct_meters[4:])
        weekly_list.append({data_oct_meters[0]['hour']: sum(
            item['value'] for item in data_oct_meters[4:])})

    if len(data_oct_meters) == 4:
        interval_cc = datetime.strptime(str(data_oct_meters[0]['hour'])[:16], '%Y-%m-%d %H:%M')
        writer.writerow([datetime.now(), datetime.now(), int(self.id), meters[0].id, sum(
            item['value'] for item in data_oct_meters), interval_cc, timedelta(hours=1), 'kWh'])
        peak_list.append({'interval_start': interval_cc, 'value': sum(
            item['value'] for item in data_oct_meters)})
        weekly_list.append({data_oct_meters[0]['hour']: sum(
            item['value'] for item in data_oct_meters)})

    upload_db(stream)
    return peak_list, weekly_list
