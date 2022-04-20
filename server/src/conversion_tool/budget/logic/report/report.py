from datetime import datetime, timedelta, time
import calendar
from collections import OrderedDict
from dateutil.rrule import rrule, MONTHLY
from collections import defaultdict
from operator import itemgetter
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils.timezone import override as override_timezone
import pytz
from pytz import country_timezones
import StringIO
import xlsxwriter
from itertools import groupby
from django.core.files.base import ContentFile
from xlrd import open_workbook, xldate
from budget import *
from month import *
from core.models import *
from write_data import *
from weekly import *
from ..db.season import upload_season


def produce_budget_report(self, budget_data, cc_med_data):
    cet = pytz.timezone('CET')
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    # text_format = workbook.add_format()
    # text_format.set_text_wrap()
    # Widen column A for extra visibility.
    # worksheet.set_column('A:A', 10)
    bold_format = workbook.add_format({'bold': True})
    # blue_format = workbook.add_format({'bold': True, 'color': 'blue'})
    # worksheet.write(0, 0, 'Report', bold_format)
    # worksheet.write(0, 1, self.budget_id)
    cc_from = cet.localize(datetime(self.year, 01, 01, 0, 0), is_dst=None)
    cc_to = cet.localize(datetime(self.year, 12, 31, 23, 59), is_dst=None)
    months_all = [str(dt)[:7] for dt in rrule(MONTHLY, dtstart=cc_from, until=cc_to)]
    # print 'months = ', months_all
    sheet_col = {}
    for i, month in enumerate(months_all):
        worksheet.write(2, 3 + i, month)
        sheet_col[month] = 3 + i
    total = []
    total_max = []
    peak_list = []
    headge_list = []
    cc_list = []
    peak_month = []
    peak_month_list = []
    peak_season = []
    peak_cc_season = []
    # shedules = Shedule.objects.all()
    if len(self.offer.shedules.all()) == 1:
        shedules = Shedule.objects.filter(id__in=[1,2])
    else:
        shedules = self.offer.shedules.all()

    # print 'shedules ===== ', shedules
    stream = StringIO.StringIO()
    writer = csv.writer(stream, delimiter='\t')
    for index, shedule in enumerate(shedules):
        peak_list, headge_list = peak_data(self, shedule, budget_data)
        cc_list = cc_data(self, shedule, cc_med_data)
        peak_month, peak_month_list = medium_month(peak_list)
        peak_season = medium_season(peak_month_list)
        peak_cc_season = med_cc_season(cc_list)
        # weekly_headge(self, shedule, headge_list)
        upload_budget_med(self, shedule, peak_season, peak_cc_season)
        worksheet, total, total_max = write_months(sheet_col, index, shedule, len(shedules), months_all,  peak_month, worksheet, bold_format)
        worksheet = write_max_months(max_month(total_max), sheet_col, worksheet)
        worksheet = write_season(self, worksheet, writer, shedule, len(shedules), index, peak_season, bold_format)
    upload_season(stream)
    workbook.close()
    # data = ContentFile(output.getvalue())
    # self.budget_report.save(
    #     name='{}.xlsx'.format(self.year),
    #     content=data,
    #     save=False
    # )
    self.save()
