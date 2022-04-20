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

def upload_profile_type(self, data_file):
    stream = StringIO.StringIO()
    writer = csv.writer(stream, delimiter='\t')
    wb = open_workbook(data_file.name)
    sheet_values = {}
    sheet = wb.sheet_by_index(0)
    print 'nr of collomns === ', sheet.ncols
    print 'nr of rows === ', sheet.nrows
    for row in range(1, sheet.nrows):
        # print str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:16], sheet.cell(row, 1).value
        interval_cc = pytz.utc.localize(datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:16], '%Y-%m-%d %H:%M'))
        interval_start_cc = interval_cc.astimezone(pytz.timezone('UTC'))
        # print interval_start_cc , type(interval_start_cc), float(sheet.cell(row, 1).value), type(self.id), type(timedelta(hours=1))
        writer.writerow([datetime.now(), datetime.now(), self.id, Decimal(sheet.cell(row, 1).value), interval_start_cc, timedelta(hours=1)])
    upload_db(stream)
