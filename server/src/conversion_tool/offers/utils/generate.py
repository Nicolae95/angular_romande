from rest_framework import serializers
from django.template import Context
from django.template.loader import render_to_string, get_template
from companies.models import Meter, Site, Company
from django.http import HttpRequest
from django_countries.fields import CountryField
from datetime import datetime, timedelta, time
from math import sqrt
import csv
import json
import pytz
import StringIO
import io
import copy
from django.db.models import Sum, F
from offers.models import *
from translations.models import *
from type.serializers import *
from typepondere.serializers import *
from core.serializers import *
from pfc.serializers import *
from core.models import *
from companies.serializers import *
from budget.models import *
from type.models import *
from typepondere.models import *
from core.logic.db.upload import *



def generate_cc_budgets(self, validated_data, obj):
    cet = pytz.timezone('UTC')
    print 'validated_data function = ', validated_data['pfc']
    meds = []
    days = []
    data_year = int(validated_data['cc'].site.year)
    transaction_years = map(lambda x: data_year + x, range(1,6))
    for year in obj.years.split(','):
        cet_cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        cet_cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        print 'cc == ', validated_data['cc']
        liss = False
        lis_value = 0
        if validated_data['lissage_years']:
            try:
                lis_data = validated_data['lissage_years']['lissage_years']['lissage']
                print 'lisssssssssssssss dataaaaaaaaaaaaa = ', lis_data
                liss = True
                for lissag in lis_data:
                  for key, lis in lissag.iteritems():
                    print 'lisassssage key and value =========== ', key, lis
                    if str(key) == str(year):
                        lis_value = lis
                        print 'lisassssage value =========== ', lis_value, lis
                # print 'lis budget value == ', lis_value
            except:
                lis_value = 0
        budget = Budget.objects.create(year = int(year),
                                       budget_id = validated_data['name'],
                                       offer = obj,
                                       pfc = validated_data['pfc'],
                                       pfc_market = validated_data['pfc_market'],
                                       cc = validated_data['cc'],
                                       unit = validated_data['unit'],
                                       lissage = liss
                                       )
        budget.produce_report()
        bgrecord = BudgetRecord.objects.filter(budget = budget).aggregate(Sum('value'))
        if int(year) in transaction_years:
            crecord = TranslationRecord.objects.filter(meter = validated_data['cc'],
                                                       interval_start__gte=cet_cc_from,
                                                       interval_start__lte=cet_cc_to
                                                       ).aggregate(Sum('value'))
        else :
            crecord = EnergyConsumptionRecord.objects.filter(meter = validated_data['cc'],
                                                             interval_start__gte=cet_cc_from,
                                                             interval_start__lte=cet_cc_to
                                                             ).aggregate(Sum('value'))
        # constants = Constants.objects.all().aggregate(Sum('value'))
        # if constants['value__sum'] == None:
        #     csum = 0
        # else:
        #     csum = constants['value__sum']
        parameters = ParameterRecord.objects.filter(offer = obj, year=int(year)).aggregate(Sum('value'))

        try:
            prix = RiscRecord.objects.get(risc = Risc.objects.get(name='Risque prix'), year = int(year), pfc=validated_data['pfc'])
            if prix:
                prixv = prix.value * sqrt(int(validated_data['validation_time']))
                print 'prix rad', prixv
            else:
                prixv = 0
        except:
            prixv = 0

        try:
            risc_record = RiscRecord.objects.filter(risc = Risc.objects.get(name='Risque PwB'),  pfc = validated_data['pfc'], year=int(year)).aggregate(Sum('value'))
            if risc_record['value__sum'] == None:
                rsum = 0
            else:
                rsum = risc_record['value__sum']
        except:
            rsum = 0

        try:
            risv = RiscRecord.objects.get(pfc=validated_data['pfc'],
                                        year = int(year),
                                        risc = Risc.objects.get(name__icontains='Risque volume')
                                        ).value
        except:
            risv = 0

        riscvf = 0
        riscvs = 0
        if int(year) < 2020:
            riscvf = risv
        else:
            riscvs = risv

        try:
            risceco = RiscRecord.objects.get(pfc=validated_data['pfc'],
                                          year = int(year),
                                          risc = Risc.objects.get(code=obj.energy_type)
                                          ).value
        except:
            risceco = 0

        if crecord['value__sum']:
            vsum = crecord['value__sum']
        else:
            vsum = 1
        if parameters['value__sum'] == None:
            psum = 0
        else:
            psum = parameters['value__sum']
        if bgrecord['value__sum'] == None:
            bsum = 0
        else:
            bsum = bgrecord['value__sum']

        try:
            parameters = ParameterRecord.objects.filter(offer = obj, year=int(year), parameter=Parameter.objects.get(code='efforts')).aggregate(Sum('value'))
            if parameters['value__sum'] == None:
                pfsum = 0
            else:
                pfsum = parameters['value__sum']
        except:
            pfsum = 0

        print 'lisssssssssssss value === ', lis_value
        BudgetAveragePerYear.objects.create(year=int(year), value=((bsum/float(vsum)) / float(10.0)) + prixv + rsum + riscvf + pfsum, budget=budget)
        BudgetAveragePerYearRiscs.objects.create(year=int(year), value=((bsum/float(vsum)) / float(10.0)) + prixv + rsum + riscvf + psum + lis_value + riscvs + risceco, budget=budget)
