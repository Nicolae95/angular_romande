import xlsxwriter
from xlrd import open_workbook, xldate
from datetime import datetime, timedelta, time
import numpy as np


def write_months(sheet_col, index, shedule, shedules, months_all, peak_data_res, worksheet, bold_format):
    total = []
    total_max = []
    total_peak = 0
    # worksheet.write(3, 2, 'MaxH', bold_format)
    # worksheet.write(4 + index, 2, shedule.title, bold_format)
    # worksheet.write(9 + shedules + index, 8, shedule.title, bold_format)
    for p, value in enumerate(peak_data_res):
        total_peak += value['value']
        # worksheet.write(4+index, sheet_col[value['month']], value['value'])
        total.append({value['month']: value['value']})
        total_max.append({value['month']: value['max']})
        # print sheet_col[value['month']], value['value']
    return worksheet, total, total_max


def write_max_months(total_max_data_res, sheet_col, worksheet):
    # for p, m in enumerate(total_max_data_res):
        # worksheet.write(3, sheet_col[m['month']], m['max'])
        # print sheet_col[m['month']], m['max']
    return worksheet


def write_season(self, worksheet, writer, shedule, shedules, index, peak_data_med_res, bold_format):
    # worksheet.write(shedules + 8, 9, 'Summer', bold_format)
    # worksheet.write(shedules + 8, 10, 'Winter', bold_format)
    # worksheet.write(9 + shedules + index, 8, shedule.title, bold_format)
    # worksheet.write(9 + shedules + index, 9, sum(item for item in peak_data_med_res['summer']))
    # worksheet.write(9 + shedules + index, 10, sum(item for item in peak_data_med_res['winter']))
    writer.writerow([datetime.now(), int(self.id), int(self.year), 'Summer', shedule.id, sum(item for item in peak_data_med_res['summer']), 'Eu/MWh'])
    writer.writerow([datetime.now(), int(self.id), int(self.year), 'Winter', shedule.id, sum(item for item in peak_data_med_res['winter']), 'Eu/MWh'])
    return worksheet
