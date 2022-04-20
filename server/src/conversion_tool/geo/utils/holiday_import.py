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


def upload_holidays(self, data_file):
    reader = csv.reader(data_file)
    csv_list = list(reader)
    print 'nr of collomns === ', len(csv_list[0])
    print 'nr of rows === ', len(csv_list)
    Holiday = apps.get_model("geo", "Holiday")
    for row in range(1, len(csv_list)):
        for col in range(1, len(csv_list[0])):
            date = datetime.strptime(str(csv_list[row][col]), '%d.%m.%Y')
            Holiday.objects.create(title=csv_list[0][col], date=date, country=self.region.country, region=self.region)
        
