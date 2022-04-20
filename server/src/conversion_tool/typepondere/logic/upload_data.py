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
from decimal import *


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


def upload_pondere(self, data_file):
    stream = StringIO.StringIO()
    writer = csv.writer(stream, delimiter='\t')
    wb = open_workbook(data_file.name)
    sheet_values = {}
    sheet = wb.sheet_by_index(0)
    print 'nr of collomns === ', sheet.ncols
    print 'nr of rows === ', sheet.nrows
    FMT = '%H:%M'
    td = datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell(2, 0).value, 0))[11:16], FMT) - datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell(1, 0).value, 0))[11:16], FMT)
    print td, str(td) == '0:15:00'
    if str(td) == '0:15:00':
        data_meters = []
        data_octb_meters = []
        for row in range(1, sheet.nrows):
            hour = (str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:14] + '00')
            if hour[5:] == get_oct_sunday(self.year) + ' 02:00':
                data_octb_meters.append({'hour': hour, 'value': sheet.cell(row, 1).value})
            else:
                data_meters.append({hour: sheet.cell(row, 1).value})
        data_hour = defaultdict(list)
        
        for meter in data_meters:
            for k, value in meter.iteritems():
                data_hour[k].append(value)
        # print 'data_hour == ', data_hour
        for key in data_hour.keys():
            interval_start_cc = datetime.strptime(str(key)[:16], '%Y-%m-%d %H:%M')
            # print data_hour[key], sum(data_hour[key])
            writer.writerow([datetime.now(), datetime.now(), self.id, sum(data_hour[key]), interval_start_cc, timedelta(hours=1)])
        
        if len(data_octb_meters) == 8:
            interval_cc = datetime.strptime(str(data_octb_meters[0]['hour'])[:16], '%Y-%m-%d %H:%M')
            # print 'ora 02 00 ================================================== ', interval_cc, sum(item['value'] for item in data_octb_meters[:4])
            writer.writerow([datetime.now(), datetime.now(), int(self.id), sum(item['value'] for item in data_octb_meters[:4]), interval_cc, timedelta(hours=1)])
            writer.writerow([datetime.now(), datetime.now(), int(self.id), sum(item['value'] for item in data_octb_meters[4:]), interval_cc, timedelta(hours=1)])
    
        if len(data_octb_meters) == 4:
            interval_cc = datetime.strptime(str(data_octb_meters[0]['hour'])[:16], '%Y-%m-%d %H:%M')
            writer.writerow([datetime.now(), datetime.now(), int(self.id), sum(item['value'] for item in data_octb_meters), interval_cc, timedelta(hours=1)])

    else:
        for row in range(1, sheet.nrows):
            # print str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:16], sheet.cell(row, 1).value
            interval_cc = pytz.utc.localize(datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:16], '%Y-%m-%d %H:%M'))
            interval_start_cc = interval_cc.astimezone(pytz.timezone('UTC'))
            # print interval_start_cc , type(interval_start_cc), float(sheet.cell(row, 1).value), type(self.id), type(timedelta(hours=1))
            writer.writerow([datetime.now(), datetime.now(), self.id, Decimal(sheet.cell(row, 1).value), interval_start_cc, timedelta(hours=1)])
    upload_db(stream)
