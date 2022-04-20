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
from ..db.upload import upload_pfc_db
from offers.models import *


def upload_pfc_csv(id, pfc, data_file):
    streampfc = StringIO.StringIO()
    writerpfc = csv.writer(streampfc, delimiter='\t')
    reader = csv.reader(data_file)
    csv_list = list(reader)
    rows = []
    for row in range(3, len(csv_list)):
        for col in range(len(csv_list[row])):
            if col in [0,3,6,9]:
                if csv_list[row][col] != '':
                    print datetime.strptime(csv_list[row][col], '%d.%m.%Y %H:%M'), csv_list[row][col+1]
                    interval_pfc = pytz.utc.localize(datetime.strptime(csv_list[row][col], '%d.%m.%Y %H:%M'))
                    interval_start_pfc = interval_pfc.astimezone(pytz.timezone('CET'))
                    writerpfc.writerow([datetime.now(), datetime.now(), int(id), int(pfc.id), float(csv_list[row][col+1].replace(',', '.')), interval_start_pfc, timedelta(hours=1), 'CHF'])
    upload_pfc_db(streampfc)


def upload_pfc_xls(id, pfc, data_file):
    cet = pytz.timezone('CET')
    streampfc = StringIO.StringIO()
    writerpfc = csv.writer(streampfc, delimiter='\t')
    wb = open_workbook(data_file.name)
    sheet_values = {}
    sheet = wb.sheet_by_index(0)
    print 'nr of collomns === ', sheet.ncols
    print 'nr of rows === ', sheet.nrows
    risc, created = Risc.objects.get_or_create(name=sheet.cell(17, 3).value)
    risc1, created1 = Risc.objects.get_or_create(name=sheet.cell(18, 3).value)
    risc2, created2 = Risc.objects.get_or_create(name=sheet.cell(19, 3).value)

    energy1, created3 = Risc.objects.get_or_create(code='energy1')
    energy2, created4 = Risc.objects.get_or_create(code='energy2')
    energy3, created5 = Risc.objects.get_or_create(code='energy3')
    energy4, created6 = Risc.objects.get_or_create(code='energy4')
    energy5, created7 = Risc.objects.get_or_create(code='energy5')
    energy6, created8 = Risc.objects.get_or_create(code='energy6')

    data_year = int(datetime.now().year)
    years = map(lambda x: data_year + x, range(0,6))

    for row in [17, 18, 19, 21, 22, 23, 24, 25, 26]:
        for col in range(4,8):
            # print 'risc col = ', col
            if row == 17:
                RiscRecord.objects.create(risc=risc, value=float(sheet.cell(row, col).value), pfc=pfc, year=data_year+col-3)
            if row == 18:
                RiscRecord.objects.create(risc=risc1, value=float(sheet.cell(row, col).value), pfc=pfc, year=data_year+col-3)
            if row == 19:
                RiscRecord.objects.create(risc=risc2, value=float(sheet.cell(row, col).value), pfc=pfc, year=data_year+col-3)
            if row == 21:
                RiscRecord.objects.create(risc=energy1, value=float(sheet.cell(row, col).value), pfc=pfc, year=data_year+col-3)
            if row == 22:
                RiscRecord.objects.create(risc=energy2, value=float(sheet.cell(row, col).value), pfc=pfc, year=data_year+col-3)
            if row == 23:
                RiscRecord.objects.create(risc=energy3, value=float(sheet.cell(row, col).value), pfc=pfc, year=data_year+col-3)
            if row == 24:
                RiscRecord.objects.create(risc=energy4, value=float(sheet.cell(row, col).value), pfc=pfc, year=data_year+col-3)
            if row == 25:
                RiscRecord.objects.create(risc=energy5, value=float(sheet.cell(row, col).value), pfc=pfc, year=data_year+col-3)
            if row == 26:
                RiscRecord.objects.create(risc=energy6, value=float(sheet.cell(row, col).value), pfc=pfc, year=data_year+col-3)

    if sheet.cell(1, 2).value:
        cols = 3
    else:
        cols = 2

    for col in range(1, cols):
        rows = []
        for row in range(1, sheet.nrows):
            if sheet.cell(row, col).value != '' :
                # try:
                dat = str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:13]+':00'
                # dat = pytz.utc.localize(datetime.strptime(dats, '%Y-%m-%d %H:%M'))
                # dat = interval_pfc.astimezone(pytz.timezone('UTC'))
                # except:
                #     dats = datetime.strptime(str(sheet.cell(row, 0).value), '%d.%m.%Y %H:%M')
                #     datnaive = datetime.strptime(dats, '%Y-%m-%d %H:%M')
                #     datt = cet.localize(datnaive, is_dst=None)
                #     dat = make_aware(datt.replace(tzinfo=None), cet, is_dst=None)
                # print 'date time = ', dat, dat.astimezone(pytz.timezone('UTC'))
                if col == 1:
                    writerpfc.writerow([datetime.now(), datetime.now(), int(id), int(pfc.id), float(sheet.cell(row, col).value), dat, timedelta(hours=1), 'CHF'])
                    # print(float(sheet.cell(row, col).value), dat, 'CHF')
                elif col == 2:
                    writerpfc.writerow([datetime.now(), datetime.now(), int(id), int(pfc.id), float(sheet.cell(row, col).value), dat, timedelta(hours=1), 'EUR'])
                    # print(float(sheet.cell(row, col).value), dat, timedelta(hours=1), 'EUR')
    upload_pfc_db(streampfc)


    # streampfc = StringIO.StringIO()
    # writerpfc = csv.writer(streampfc, delimiter='\t')
    # wb = open_workbook(data_file.name)
    # sheet_values = {}
    # sheet = wb.sheet_by_index(0)
    # print 'nr of collomns === ', sheet.ncols
    # print 'nr of rows === ', sheet.nrows
    #
    # for row in range(3, sheet.nrows):
    #     for col in range(sheet.ncols):
    #         if col in [0,3,6,9]:
    #             if sheet.cell(row, col).value != '':
    #                 dat = str(xldate.xldate_as_datetime(sheet.cell(row, col).value, 0))
    #                 # interval_pfc = pytz.utc.localize(dat, '%Y-%m-%d %H:%M')
    #                 # interval_start_pfc = interval_pfc.astimezone(pytz.timezone('CET'))
    #                 writerpfc.writerow([datetime.now(), datetime.now(), int(id), int(pfc.id), float(sheet.cell(row, col+1).value), dat, timedelta(hours=1), 'CHF'])
    # upload_pfc_db(streampfc)
