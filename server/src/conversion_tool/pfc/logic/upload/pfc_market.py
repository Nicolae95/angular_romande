from datetime import datetime, timedelta, time
from django.db.models import Q, Func, Sum, Max, Count
import StringIO
import xlsxwriter
from contextlib import closing
from django.db import connection
from xlrd import open_workbook, xldate
import csv
import pytz
from pytz import country_timezones
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils.timezone import override as override_timezone
from collections import defaultdict
from operator import itemgetter
from ..db.upload import *
from offers.models import *

def upload_pfc_csv_market(id, pfc, data_file):
    streampfc = StringIO.StringIO()
    writerpfc = csv.writer(streampfc, delimiter='\t')
    reader = csv.reader(data_file)
    csv_list = list(reader)
    for col in range(1,3):
        rows = []
        for row in range(1, len(csv_list)):
            if csv_list[row][col] != '' :
                print 'pfc market = ', datetime.strptime(csv_list[row][0], '%d.%m.%Y %H:%M'), csv_list[row][col], str(csv_list[0][col])[-7:]
                interval_pfc = pytz.utc.localize(datetime.strptime(csv_list[row][0], '%d.%m.%Y %H:%M'))
                interval_start_pfc = interval_pfc.astimezone(pytz.timezone('UTC'))
                # print str(csv_list[0][col])[-7:]
                writerpfc.writerow([datetime.now(), datetime.now(), int(id), int(pfc.id), float(csv_list[row][col].replace(',', '.')), interval_start_pfc, timedelta(hours=1), 'CHF'])
    upload_pfc_market_db(streampfc)


def upload_pfc_xls_market(id, pfc, data_file):
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
    # energy7, created9 = Risc.objects.get_or_create(code='energy7')
    # energy8, created10 = Risc.objects.get_or_create(code='energy8')
    # energy9, created11 = Risc.objects.get_or_create(code='energy9')

    data_year = int(datetime.now().year)
    years = map(lambda x: data_year + x, range(0,6))

    for row in [17, 18, 19, 21, 22, 23, 24, 25, 26]:
        for col in range(4,8):
            if row == 17:
                RiscRecord.objects.create(risc=risc, value=float(sheet.cell(row, col).value), pfc_market=pfc, year=data_year+col-3)
            if row == 18:
                RiscRecord.objects.create(risc=risc1, value=float(sheet.cell(row, col).value), pfc_market=pfc, year=data_year+col-3)
            if row == 19:
                RiscRecord.objects.create(risc=risc2, value=float(sheet.cell(row, col).value), pfc_market=pfc, year=data_year+col-3)
            if row == 21:
                RiscRecord.objects.create(risc=energy1, value=float(sheet.cell(row, col).value), pfc_market=pfc, year=data_year+col-3)
            if row == 22:
                RiscRecord.objects.create(risc=energy2, value=float(sheet.cell(row, col).value), pfc_market=pfc, year=data_year+col-3)
            if row == 23:
                RiscRecord.objects.create(risc=energy3, value=float(sheet.cell(row, col).value), pfc_market=pfc, year=data_year+col-3)
            if row == 24:
                RiscRecord.objects.create(risc=energy4, value=float(sheet.cell(row, col).value), pfc_market=pfc, year=data_year+col-3)
            if row == 25:
                RiscRecord.objects.create(risc=energy5, value=float(sheet.cell(row, col).value), pfc_market=pfc, year=data_year+col-3)
            if row == 26:
                RiscRecord.objects.create(risc=energy6, value=float(sheet.cell(row, col).value), pfc_market=pfc, year=data_year+col-3)
    
    if sheet.cell(1, 2).value:
        cols = 3
    else:
        cols = 2

    for col in range(1, cols):
        rows = []
        for row in range(1, sheet.nrows):
            if sheet.cell(row, col).value != '' :
                dat = str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:13]+':00'
                if col == 1:
                    writerpfc.writerow([datetime.now(), datetime.now(), int(id), int(pfc.id), float(sheet.cell(row, col).value), dat, timedelta(hours=1), 'CHF'])
                    # print(float(sheet.cell(row, col).value), dat, 'CHF')
                elif col == 2:
                    writerpfc.writerow([datetime.now(), datetime.now(), int(id), int(pfc.id), float(sheet.cell(row, col).value), dat, timedelta(hours=1), 'EUR'])
                    # writerpfc.writerow([datetime.now(), datetime.now(), int(id), int(pfc.id), float(sheet.cell(row, col).value), dat, timedelta(hours=1), 'CHF'])
    
    upload_pfc_market_db(streampfc)
