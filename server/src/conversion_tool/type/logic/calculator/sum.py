# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytz
import os
from os.path import basename
from collections import defaultdict
from operator import itemgetter
from xlrd import open_workbook, xldate
import xlsxwriter
from datetime import datetime, timedelta
import StringIO
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from translate import Translation

def to_datetime(xldate):
    # temp = datetime(1900, 1, 1)
    temp = datetime(1899, 12, 30)
    delta = timedelta(days=xldate)
    return temp + delta + timedelta(minutes=1)


def to_date(date):
    return datetime.strptime(str(date)[:16], '%Y-%m-%d %H:%M')


class Parsing:
    files = []
    diff = None
    diff_hour_file = {}

    ftype = ''
    hour_files = []
    fourth_files = []
    coverted_data_files = []
    data_files = []

    
    def __init__(self, files, ftype, diff=None):
        self.files = files
        self.ftype = ftype
        self.diff = diff
        if self.files:
            for file in self.files:
                wb = open_workbook(file)
                sheet_values = {}
                sheet = wb.sheet_by_index(0)
                print 'sheet name = ', sheet.name
                print 'nr of collomns === ', sheet.ncols
                print 'nr of rows === ', sheet.nrows
                FMT = '%H:%M'
                td = datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell_value(2, 0), 0))[
                                    11:16], FMT) - datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell_value(1, 0), 0))[11:16], FMT)
                print td
                if str(td) == '0:15:00':
                    self.fourth_files.append(file)
                    self.coverted_data_files.append(self.convert_hour_site(file, sheet))
                else:
                    self.hour_files.append(file)
                    self.data_files.append(self.hour_site(file, sheet))


    def convert_hour_site(self, file, sheet):
        data_meters = []
        for row in range(1, sheet.nrows):
            hour = str(to_datetime(sheet.cell(row, 0).value))[:14] + '00'
            data_meters.append({hour: sheet.cell_value(row, 1)})
        
        target = open(file, 'w')
        target.truncate()
        
        workbook = xlsxwriter.Workbook(file, {'default_date_format': 'dd/mm/yyyy hh:mm'})
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:A', 20)

        data_hour = defaultdict(list)
        for meter in data_meters:
            for k, value in meter.iteritems():
                data_hour[k].append(value)

        data = defaultdict(list)
        trans_data = []
        for index, key in enumerate(sorted(data_hour.keys())):
            # data[key] = sum(item for item in data_hour[key])
            if data_hour[key] == 8:
                fsum = sum(item for item in data_hour[key][:4])
                ssum = sum(item for item in data_hour[key][4:])
                data[key].append(fsum)
                worksheet.write(index+1, 0, to_date(key))
                worksheet.write(index+1, 1, sum(item for item in data_hour[key]))
                if self.ftype == 'translate':
                    trans_data.append({'value': sum(item for item in data_hour[key]), 'interval_start': to_date(key)})
            else:
                data[key].append(sum(item for item in data_hour[key]))
                worksheet.write(index+1, 0, to_date(key))
                worksheet.write(index+1, 1, sum(item for item in data_hour[key]))
                if self.ftype == 'translate':
                    trans_data.append({'value': sum(item for item in data_hour[key]), 'interval_start': to_date(key)})
        # worksheet.write_column('A', sorted(data_hour.keys()))
        workbook.close()
        return {'file': file, 'data': data}


    def hour_site(self, file, sheet):
        data_hour = defaultdict()
        trans_data = []
        for row in range(1, sheet.nrows):
            hour = str(to_datetime(sheet.cell(row, 0).value))[:14] + '00'
            data_hour[hour] = sheet.cell_value(row, 1)
            if self.ftype == 'translate':
                trans_data.append({'value': sheet.cell_value(row, 1), 'interval_start': to_date(hour)})
        # print(data_hour)
        return {'file': file, 'data': data_hour, 'trans_data': trans_data}


    def converted_data(self):
        return self.coverted_data_files + self.data_files


    def calculate_sum_site(self):
        data = self.converted_data()
        all_data = defaultdict(list)
        self.sum_data = defaultdict()
        self.trans_data = []
        output = StringIO.StringIO()
        workbook_sum = xlsxwriter.Workbook(output, {'in_memory': True, 'default_date_format': 'dd/mm/yyyy hh:mm'})
        worksheet_sum = workbook_sum.add_worksheet()
        worksheet_sum.set_column('A:A', 20)

        for objf in data:
            for key in objf['data'].keys():
                all_data[key].append(objf['data'][key])
        
        for index, key in enumerate(sorted(all_data.keys())):
            if self.diff:
                self.sum_data[key] = sum(item for item in all_data[key])
            else:
                worksheet_sum.write(index+1, 0, to_date(key))
                worksheet_sum.write(index+1, 1, sum(item for item in all_data[key]))
            
            if self.ftype == 'translate':
                self.trans_data.append({'value': sum(item for item in all_data[key]), 'interval_start': to_date(key)})


        workbook_sum.close()
        if self.diff == None:
            data = ContentFile(output.getvalue())
            fs = FileSystemStorage(location='media/calculator/')
            filename = fs.save('sum.xlsx', data)
        else:
            filename = None
        return filename


    def calculate_diff_site(self):
        filename = self.calculate_sum_site()

        if self.diff:
            wb = open_workbook(self.diff)
            sheet_values = {}
            sheet = wb.sheet_by_index(0)
            FMT = '%H:%M'
            td = datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell_value(2, 0), 0))[
                                11:16], FMT) - datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell_value(1, 0), 0))[11:16], FMT)
            print td
            if str(td) == '0:15:00':
                self.fourth_files.append(self.diff)
                self.diff_hour_file = self.convert_hour_site(self.diff, sheet)
            else:
                self.hour_files.append(self.diff)
                self.diff_hour_file = self.hour_site(self.diff, sheet)
            
            target = open(self.diff, 'w')
            target.truncate()

            workbook = xlsxwriter.Workbook(self.diff, {'default_date_format': 'dd/mm/yyyy hh:mm'})
            worksheet = workbook.add_worksheet()
            worksheet.set_column('A:A', 20)

            for index, key in enumerate(sorted(self.diff_hour_file['data'].keys())):
                worksheet.write(index+1, 0, to_date(key))
                worksheet.write(index+1, 1, self.diff_hour_file['data'][key] - self.sum_data[key])
            workbook.close()
        return self.diff


    def translate_site(self, year, years_value):
        sum_file = self.calculate_sum_site()
        # self.sum_data
        file_name = os.path.basename(sum_file)
        target = open(file_name, 'w')
        target.truncate()

        workbook = xlsxwriter.Workbook(file_name, {'default_date_format': 'dd/mm/yyyy hh:mm'})
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:A', 20)
        
        translate = Translation(self.trans_data, year, years_value, worksheet)
        worksheet = translate.worksheet
        workbook.close()
        
        return sum_file

    # def translate_data(self, years, translation):
    #     if self.files:
    #         data = self.converted_data()
    #         for obj in data:
    #             target = open(obj['file'], 'w')
    #             target.truncate()
    #             workbook = xlsxwriter.Workbook((obj['file'], {'default_date_format': 'dd/mm/yyyy hh:mm'}))
    #             worksheet = workbook.add_worksheet()
    #             translation = Translation(obj['trans_data'], years)
    #             workbook.close()


class ParsingMultisite:

    def __init__(self, file, diff=None):
        self.file = file
        self.diff = diff
        if self.file:
            wb = open_workbook(self.file)
            sheet_values = {}
            sheet = wb.sheet_by_index(0)
            print 'sheet name = ', sheet.name
            print 'nr of collomns === ', sheet.ncols
            print 'nr of rows === ', sheet.nrows
            FMT = '%H:%M'
            td = datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell_value(2, 0), 0))[
                11:16], FMT) - datetime.strptime(str(xldate.xldate_as_datetime(sheet.cell_value(1, 0), 0))[11:16], FMT)
            print td
            if str(td) == '0:15:00':
                self.convert_hour_multisite(file, sheet)
            else:
                self.hour_multisite(file, sheet)


    def convert_hour_multisite(self, file, sheet):
        data_meters = defaultdict(list)
        for row in range(1, sheet.nrows):
            for col in range(1, sheet.ncols):
                data_meters[str(col)].append({str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:10] + ' '
                                              + str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[11:14] + '00': sheet.cell(row, col).value})
        self.data_sum = defaultdict()

        target = open(file, 'w')
        target.truncate()

        workbook = xlsxwriter.Workbook(file, {'default_date_format': 'dd/mm/yyyy hh:mm'})
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:A', 20)
        
        self.all_sum = defaultdict(list)

        for meter in data_meters:
            data_hour = defaultdict(list)
            data_meter = defaultdict()
            for di in data_meters[meter]:
                for k, value in di.iteritems():
                    data_hour[k].append(value)
            for index, key in enumerate(sorted(data_hour.keys())):
                # interval_cc = datetime.strptime(str(key)[:16], '%Y-%m-%d %H:%M')
                # print {'value': sum(item for item in data_hour[key]), 'time': key}
                self.all_sum[key].append(sum(item for item in data_hour[key]))
                data_meter[key] = sum(item for item in data_hour[key])
                if int(meter) == 1:
                    worksheet.write(index+1, 0, to_date(key))
                worksheet.write(index+1, int(meter), format(data_meter[key], '.8f'))
            self.data_sum[meter] = data_meter
        workbook.close()
        # print self.data_sum.keys()


    def hour_multisite(self, file, sheet):
        data_meters = defaultdict(list)
        for row in range(1, sheet.nrows):
            for col in range(1, sheet.ncols):
                data_meters[str(col)].append({str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[:10] + ' '
                                              + str(xldate.xldate_as_datetime(sheet.cell(row, 0).value, 0))[11:14] + '00': sheet.cell(row, col).value})
        self.all_sum = defaultdict(list)
        self.data_sum = defaultdict()
        for meter in data_meters:
            data_hour = defaultdict()
            for di in data_meters[meter]:
                for k, value in di.iteritems():
                    self.all_sum[key].append(value)
                    data_hour[k] = value
            self.data_sum[meter] = data_hour

    def converted_data(self):
        return self.file

    def calculate_sum(self):
        output = StringIO.StringIO()
        workbook_sum = xlsxwriter.Workbook(output, {'in_memory': True, 'default_date_format': 'dd/mm/yyyy hh:mm'})
        worksheet_sum = workbook_sum.add_worksheet()
        worksheet_sum.set_column('A:A', 20)

        self.data_sum = defaultdict()
        for index, key in enumerate(sorted(self.all_sum.keys())):
            if self.diff:
                self.data_sum[key] = sum(item for item in self.all_sum[key])
            else:
                worksheet_sum.write(index+1, 0, to_date(key))
                worksheet_sum.write(index+1, 1, sum(item for item in self.all_sum[key]))

        workbook_sum.close()
        if self.diff == None:
            data = ContentFile(output.getvalue())
            fs = FileSystemStorage(location='media/calculator/')
            filename = fs.save('multisite_sum.xlsx', data)
        else:
            filename = None
        return filename
