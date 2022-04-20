# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import *
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.template.loader import get_template
from collections import defaultdict
from django.core.files.images import ImageFile
from cockpit.models import CockpitMarket, Chart
from datetime import datetime, timedelta, time
import pytz
import os
import io
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests



def generate_cockpit_mail(cockpit, charts, url):
    cet = pytz.timezone('UTC')
    today = datetime.now().date()
    dfrom = (datetime.now() - timedelta(days=30 * 4)).date()
    day_groups = defaultdict()
    date_groups = defaultdict()

    if dfrom.isoweekday() == 6:
        dfrom = dfrom + timedelta(days=2)
    elif dfrom.isoweekday() == 7:
        dfrom = dfrom + timedelta(days=1)

    tabel_chart = []
    for chart in charts:
        if chart.tabel:
            print list(chart.markets.all().values_list('market_id', flat=True))
            tabel_chart = tabel_chart + list(chart.markets.all().values_list('market_id', flat=True))
    tabel_chart = [str(m) for m in tabel_chart]
    stabel_chart = ','.join(tabel_chart)
    
    enrglist = {'1': 'Power', '2': 'Gas', '3': 'Coal', '4': 'Emissions', '5': 'Oil', '6': 'Rates', '7': 'Others'}
    # rtable = requests.get('http://www.marketpricesolutions.com/apitest.asp?act=datafortableromande&cid=334,11420,95,96,177,629')
    try:
        rtable = requests.get('http://www.marketpricesolutions.com/apitest.asp?act=datafortableromande&cid='+ stabel_chart)
        data_table = json.loads(rtable.text)
        endata = data_table['data']
    except:
        uids = []
        day_groups = {}
        date_groups = {}
        endata = []
    
    if endata:
        wday = data_table['days']['wday'].split(',')
        wdate = data_table['days']['wdate'].split(',')

        for index, day in enumerate(wday):
            day_groups[str(index)] = day

        for index, date in enumerate(wdate):
            date_groups[str(index)] = date

        uids = []
        for tb in data_table['data']:
            uids.append(tb['uid'])
        
        uids = list(set(uids))
    else:
        uids = []
        day_groups = {}
        date_groups = {}
    
    print uids
    print day_groups
    print date_groups
    # uid_groups = defaultdict(list)
    uid_groups = []
    # print dfrom.strftime('%d/%m/%Y'), today.strftime('%d/%m/%Y')
    for chart in charts:
        markets = list(chart.markets.all().values_list('market_id', flat=True))
        # markets = list(chart.markets.all().values_list('id', flat=True))
        markets = [str(m) for m in markets]
        smarkets = ','.join(markets)
        print markets, smarkets
        figure = io.BytesIO()
        r = requests.get('http://www.marketpricesolutions.com/apitest.asp?act=getdataforchart&cid=' +
                         smarkets + '&dfrom=' + dfrom.strftime('%d/%m/%Y') + '&dto=' + today.strftime('%d/%m/%Y'))
        json_chart = json.loads(r.text)
        plt.ylim(0, 100)
        plt.xlim(dfrom, today)
        plt.figure(figsize=(10, 6), dpi=80)
        temp = []
        for dchart in json_chart:
            temp = [{'cid': chart.id, 'name': dchart["name"], 'value': obj['value'], 'date': datetime.strptime(
                obj['date'].replace(',', '.'), '%Y.%m.%d').date()} for obj in dchart['data']]
            temp = sorted(temp, key=lambda tt: tt['date'])
            # uid_groups[str(chart.id)].append(temp[-1])
            uid_groups.append(temp[-1])
            values = []
            days = []
            for cd in temp:
                values.append(float(cd['value']))
                days.append(cd['date'])
            plt.plot(days, values, label=dchart["name"])

        print 'uid group', uid_groups
        plt.title(cockpit.name)
        plt.legend() 
        plt.savefig(figure, format="png")
        data = ImageFile(figure)
        if chart.image:
            chart.image.delete()
        chart.image.save(
            name='{}.png'.format(str(chart.id)),
            content=data,
            save=False
        )
        chart.save()
    
    print 'charts == ', charts, len(charts)

    charts_one = []
    if len(charts) == 1:
        charts_one = charts

    charts_even = []
    charts_last = []

    if len(charts) > 1 and (len(charts) % 2) == 0:
        charts_even = charts
    elif len(charts) > 1:
        charts_even = charts[:-1]
        charts_last = charts[-1]

    context = {
        "cockpit": cockpit,
        "len_cockpit": len(charts),
        "charts_one": charts_one,
        "charts_even": charts_even,
        "charts_last": charts_last,
        "charts": charts,
        "enrglist": enrglist,
        "uids": uids,
        "day_groups": day_groups,
        "date_groups": date_groups,
        "date_groups": date_groups,
        "uid_groups": uid_groups,
        "endata": endata,
        "url": url,
    }
    template = get_template('tool/mail/cockpitb.html')
    email_content = template.render(context)
    # print email_content
    return email_content
