# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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
from django.apps import apps
# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def upload(self, data_file):
    # stream = StringIO.StringIO()
    # writer = csv.writer(stream, delimiter='\t')
    wb = open_workbook(data_file.name)
    sheet_values = {}
    sheet = wb.sheet_by_index(0)
    print 'nr of collomns === ', sheet.ncols
    print 'nr of rows === ', sheet.nrows


    for row in range(2, sheet.nrows):
        GRD = apps.get_model("offers", "GRD")
        grd, created = GRD.objects.get_or_create(name=str(sheet.cell(row, 0).value),
                                                 ligne1=str(sheet.cell(row, 13).value),
                                                 ligne2=str(sheet.cell(row, 14).value),
                                                 ligne3=str(sheet.cell(row, 15).value),
                                                 ligne4=str(sheet.cell(row, 16).value),
                                                 ligne5=str(sheet.cell(row, 17).value),
                                                 ligne6=str(sheet.cell(row, 18).value),
                                                 ligne7=str(sheet.cell(row, 19).value),
                                                 ligne8=str(sheet.cell(row, 20).value),
                                                 )
