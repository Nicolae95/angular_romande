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
from hour import hour_data, hour_data_unic
from db.upload import upload_db
from companies.models import *

def upload_cc_unic_xls(self, meters, data_file):
    stream = StringIO.StringIO()
    writer = csv.writer(stream, delimiter='\t')
    wb = open_workbook(data_file.name)
    sheet_values = {}
    sheet = wb.sheet_by_index(0)
    print 'nr of collomns === ', sheet.ncols
    print 'nr of rows === ', sheet.nrows
    FMT = '%H:%M'
    td = datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell(2, 0).value, 0))[11:16], FMT) - datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell(1, 0).value, 0))[11:16], FMT)
    print td
    peak_list = []
    weekly_list = []
    # site = Site.objects.get(id)
    if str(td) == '0:15:00':
        self.site.format_donnees = timedelta(minutes=15)
        self.site.save()
        peak_list, weekly_list = hour_data_unic(self, sheet, id, self.site, meters)
    else:
        self.site.format_donnees = timedelta(hours=1)
        self.site.save()
        for row in range(1, sheet.nrows):
            # print str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:16], sheet.cell(row, 1).value
            # interval_cc = pytz.utc.localize(datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:16], '%Y-%m-%d %H:%M'))
            interval_cc = datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:16], '%Y-%m-%d %H:%M')
            # interval_start_cc = interval_cc.astimezone(pytz.timezone('UTC'))
            # print([datetime.now(), datetime.now(), int(self.id), int(meters[0].id), sheet.cell(row, 1).value, interval_start_cc, td, 'kWh'])
            writer.writerow([datetime.now(), datetime.now(), int(self.id), int(meters[0].id), sheet.cell(row, 1).value, interval_cc, td, 'kWh'])
            peak_list.append({'interval_start': interval_cc, 'value':sheet.cell(row, 1).value})
            weekly_list.append({str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:16]: sheet.cell(row, 1).value})
    upload_db(stream)
    return peak_list, weekly_list



def upload_cc_xls(self, id, site, meters, data_file):
    stream = StringIO.StringIO()
    writer = csv.writer(stream, delimiter='\t')
    wb = open_workbook(data_file.name)
    sheet_values = {}
    sheet = wb.sheet_by_index(0)
    print 'nr of collomns === ', sheet.ncols
    print 'nr of rows === ', sheet.nrows
    n_records = 0
    # meters = defaultdict(list)
    meters_id = []
    meter_sum = 0
    FMT = '%H:%M'
    td = datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell(2, 0).value, 0))[11:16], FMT) - datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell(1, 0).value, 0))[11:16], FMT)
    for meter in meters:
        if meter.meter_sum == True:
            meter_sum = meter.id
        else:
            meters_id.append(meter.id)
    
    print 'meters == ', meters_id
    print td, 'sheet = ', sheet.ncols
    peak_list = []
    weekly_list = []
    if str(td) == '0:15:00':
        site.format_donnees = timedelta(minutes=15)
        site.save()
        hour_data(sheet, id, site, meters_id, meter_sum)
    else:
        site.format_donnees = timedelta(hours=1)
        site.save()
        if sheet.ncols-1 == len(meters_id):
            cols = sheet.ncols
        elif sheet.ncols-1 == len(meters_id)+1:
            cols = sheet.ncols-1
        else:
            cols = len(meters_id)
        data_sum = defaultdict(list)

        print 'cols = ', cols
        for row in range(1, sheet.nrows):
            n_records = n_records + 1
            for col in range(1, cols):
                data_sum[str(col)].append(sheet.cell(row, col).value)
                # print str(xldate.xldate_as_datetime(sheet.cell(row, 3).value, 0))[:10]
                interval_cc = pytz.utc.localize(datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:10] + ' ' + str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[11:16], '%Y-%m-%d %H:%M'))
                interval_start_cc = interval_cc.astimezone(pytz.timezone('UTC'))
                writer.writerow([datetime.now(), datetime.now(), int(id), int(meters_id[col-1]), sheet.cell(row, col).value, interval_start_cc, td, 'kWh'])

        # if sheet.ncols-1 == len(meters_id)+1:
        #     for row in range(4, sheet.nrows):
        #         interval_cc = pytz.utc.localize(datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:10] + ' ' + str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[11:16], '%Y-%m-%d %H:%M'))
        #         interval_start_cc = interval_cc.astimezone(pytz.timezone('UTC'))
        #         # print interval_start_cc
        #         writer.writerow([datetime.now(), datetime.now(), int(id), int(
        #             meter_sum), sheet.cell(row, sheet.ncols-1).value, interval_start_cc, td, 'kWh'])

        # elif sheet.ncols-1 == len(meters_id):
        #     meters_res = []
        #     for key in data_sum.keys():
        #         meters_res.append({'value': sum(item for item in data_sum[key]), 'interval_start': key})
        #     meters_res = sorted(meters_res, key=itemgetter('interval_start'))
        #     for met in meters_res:
        #         print 'met = ', met
        #         datem = pytz.utc.localize(datetime.strptime(met['interval_start'], '%Y-%m-%d %H:%M'))
        #         writer.writerow([datetime.now(), datetime.now(), int(id), meter_sum, met['value'], datem, timedelta(hours=1), 'kWh'])
        upload_db(stream)


def upload_cc_csv(id, site, data_file):
    stream = StringIO.StringIO()
    writer = csv.writer(stream, delimiter='\t')
    reader = csv.reader(data_file)
    csv_list = list(reader)
    first = csv_list[0]
    n_records = 0
    params = []
    peak_list = []
    FMT = '%H:%M:%S'
    # print csv_list[5][4],csv_list[4][4]
    td = datetime.strptime(csv_list[5][4], FMT) - datetime.strptime(csv_list[4][4], FMT)
    meters = []
    for col in range(5,len(csv_list[0])):
        meter, created = Meter.objects.get_or_create(
        meter_id=site.name + '_' + csv_list[3][col].replace(' ', '_'), site=site)
        meters.append(meter)
    for col in range(5,len(csv_list[0])):
        # meter, created = Meter.objects.get_or_create(
        # meter_id=site.name + '_' + csv_list[3][col].replace(' ', '_'), site=site)
        for row in range(4, len(csv_list)):
            n_records = n_records + 1
            # print csv_list[row][3], csv_list[row][col]
            interval_cc = pytz.utc.localize(datetime.strptime(csv_list[row][3]+ ' ' +csv_list[row][4][:5], '%d.%m.%Y %H:%M'))
            interval = datetime.strptime(csv_list[row][3]+ ' ' +csv_list[row][4][:5], '%d.%m.%Y %H:%M')
            interval_d = make_aware(interval, pytz.timezone('UTC'), is_dst=False)
            writer.writerow([datetime.now(), datetime.now(), int(id), int(meters[col-5].id), float(csv_list[row][col].replace(',', '.')), interval_d, td, 'kWh'])
            peak_list.append({str(interval_d): float(csv_list[row][col].replace(',', '.'))})
    print n_records
    upload_db(stream)
    return peak_list
