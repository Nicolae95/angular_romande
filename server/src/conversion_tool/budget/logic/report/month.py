from collections import defaultdict
from operator import itemgetter
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils.timezone import override as override_timezone
from datetime import datetime, timedelta, time


def medium_month(peak_list):
    peak_data_list = defaultdict(list)
    peak_data_res = []
    for d in peak_list: # you can list as many input dicts as you want here
        for key, value in d.iteritems():
            peak_data_list[key].append(value)
    for key in peak_data_list.keys():
        # peak_data_res.append({'month':key, 'max' : max(item for item in peak_data_list[key]), 'value' : sum(item for item in peak_data_list[key])/ len(peak_data_list[key])-1 })
        peak_data_res.append({'month':key, 'max' : max(item for item in peak_data_list[key]), 'lenght': len(peak_data_list[key])-1, 'value' : sum(item for item in peak_data_list[key])})
    peak_data_res = sorted(peak_data_res, key=itemgetter('month'))
    return peak_data_res , peak_data_list


def max_month(total_max):
    total_max_data_list = defaultdict(list)
    total_max_data_res = []
    for d in total_max: # you can list as many input dicts as you want here
        for key, value in d.iteritems():
            total_max_data_list[key].append(value)
    for key in total_max_data_list.keys():
        total_max_data_res.append({'month':key, 'max' : max(item for item in total_max_data_list[key])})
    return sorted(total_max_data_res, key=itemgetter('month'))


def medium_season(peak_data_list):
    peak_data_med_res = defaultdict(list)
    peak_data_res_shedule = []
    for key in peak_data_list.keys():
        peak_data_res_shedule += peak_data_list[key]
        month_med = datetime.strptime(key,'%Y-%m').month
        if month_med in [4,5,6,7,8,9]:
            peak_data_med_res['summer'] += peak_data_list[key]
        else :
            peak_data_med_res['winter'] += peak_data_list[key]
    return peak_data_med_res


def med_cc_season(cc_data_list):
    cc_data_med_res = defaultdict(list)
    cc_data_res = defaultdict(list)
    cc_data_res_shedule = []
    for d in cc_data_list: # you can list as many input dicts as you want here
        for key, value in d.iteritems():
            cc_data_res[key].append(value)
    for key in cc_data_res.keys():
        # cc_data_res_shedule += cc_data_res[key]
        month_med = datetime.strptime(key,'%Y-%m').month
        if month_med in [4,5,6,7,8,9]:
            cc_data_med_res['summer'] += cc_data_res[key]
        else :
            cc_data_med_res['winter'] += cc_data_res[key]
    # print 'cc data med summer === ', float(sum(item for item in cc_data_med_res['summer']))
    # print 'cc data med winter === ', float(sum(item for item in cc_data_med_res['winter']))
    return cc_data_med_res
