import csv

from django.views.generic import View
from django.http import HttpResponse
import json
import pytz
import os
import StringIO
import xlsxwriter
from .serializers import *
from .models import *
from core.models import *
from budget.models import *
from pfc.models import *


class SomeModelCSVExportView(View):

    def get(self, request, *args, **kwargs):
        # year = self.request.query_params.get('year', None)
        # site = self.request.query_params.get('site', None)
        year = request.GET['year']
        site = request.GET['site']

        cet = pytz.timezone('utc')
        cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        cet_cc_from = make_aware(cc_from.replace(tzinfo=None), cet, is_dst=None)
        cet_cc_to = make_aware(cc_to.replace(tzinfo=None), cet, is_dst=None)
        print cet_cc_from
        print cet_cc_to
        meter = Meter.objects.get(meter_sum=True, site_id=int(site))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="translation-{}-{}.csv"'.format(str(site), year)
        writer = csv.writer(response)
        records = TranslationRecord.objects.filter(meter=meter, interval_start__gte=cet_cc_from,
                                                   interval_start__lte=cet_cc_to).values('interval_start', 'value').order_by('interval_start')
        if not records:
            records = EnergyConsumptionRecord.objects.filter(meter=meter, interval_start__gte=cet_cc_from,
                                                       interval_start__lte=cet_cc_to).values('interval_start', 'value').order_by('interval_start')
        for row in records:
            writer.writerow([row['interval_start'].strftime("%d/%m/%Y %H:%M"), row['value']])
        return response


class BudgetCSVExportView(View):
    
    def get(self, request, *args, **kwargs):

        year = request.GET['year']
        offer_id = request.GET['offer']

        cet = pytz.timezone('utc')
        cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        cet_cc_from = make_aware(cc_from.replace(tzinfo=None), cet, is_dst=None)
        cet_cc_to = make_aware(cc_to.replace(tzinfo=None), cet, is_dst=None)
        print cet_cc_from
        print cet_cc_to

        offer = Offer.objects.get(id=int(offer_id))
        print offer
        budget = Budget.objects.get(offer=offer, pfc=offer.pfc, year=int(year))
        print budget

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="budget-{}-{}.csv"'.format(
            str(offer_id), year)
        writer = csv.writer(response)
        records = BudgetRecord.objects.filter(budget=budget, interval_start__gte=cet_cc_from,
                                                   interval_start__lte=cet_cc_to).values('interval_start', 'value').order_by('interval_start')

        for row in records:
            writer.writerow([row['interval_start'].strftime("%d/%m/%Y %H:%M"), row['value']])
        return response


class PFCCSVExportView(View):

    def get(self, request, *args, **kwargs):

        year = request.GET['year']
        pfc_id = request.GET['pfc']

        cet = pytz.timezone('UTC')
        cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        cet_cc_from = make_aware(cc_from.replace(tzinfo=None), cet, is_dst=None)
        cet_cc_to = make_aware(cc_to.replace(tzinfo=None), cet, is_dst=None)
        # print cet_cc_from
        # print cet_cc_to

        pfc = PFC.objects.get(id=int(pfc_id))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pfc-{}-{}.csv"'.format(str(pfc_id), year)
        writer = csv.writer(response)
        records = PfcConsumptionRecord.objects.filter(pfc=pfc, interval_start__gte=cet_cc_from,
                                                      interval_start__lte=cet_cc_to, unit='CHF').values('interval_start', 'value').order_by('interval_start')

        for row in records:
            dat = row['interval_start'].astimezone(pytz.timezone('UTC'))
            # print dat.strftime("%d/%m/%Y %H:%M"),  row['value']
            writer.writerow([dat.strftime("%d/%m/%Y %H:%M"), row['value']])
        return response


class PFCMarketCSVExportView(View):
    
    def get(self, request, *args, **kwargs):

        pfc_id = request.GET['pfc']

        pfc = PFCMarket.objects.get(id=int(pfc_id))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pfc-market-{}.csv"'.format(str(pfc_id))
        writer = csv.writer(response)
        records = PfcMarketConsumptionRecord.objects.filter(pfc_market=pfc).values('interval_start', 'value').order_by('interval_start')

        for row in records:
            dat = row['interval_start'].astimezone(pytz.timezone('UTC'))
            # print dat.strftime("%d/%m/%Y %H:%M"),  row['value']
            writer.writerow([dat.strftime("%d/%m/%Y %H:%M"), row['value']])
        return response
