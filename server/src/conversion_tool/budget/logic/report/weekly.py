from collections import defaultdict
from operator import itemgetter
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils.timezone import override as override_timezone
from datetime import datetime, timedelta, time
import StringIO
import csv
from math import sqrt
from ..db.weekly import uploadweekly
from ..db.med import *
from offers.models import *
from core.models import *
from django.apps import apps
from django.db import models
import ast



def weekly_values(self, rec_list):
    cet = pytz.timezone('UTC')
    streamw = StringIO.StringIO()
    writer = csv.writer(streamw, delimiter='\t')
    peak_data_rec_list = defaultdict(list)
    weekly = []
    for d in rec_list: # you can list as many input dicts as you want here
        for key, value in d.iteritems():
            peak_data_rec_list[key].append(value)

    for key in peak_data_rec_list.keys():
        # data_cet = make_naive(key, cet)
        # weekday = int(datetime.strptime(data_cet[:10], '%Y-%m-%d').isoweekday())
        weekday = int(datetime.strptime(key[:10], '%Y-%m-%d').isoweekday())
        hour = int(key[11:13])
        weekly.append({(weekday-1)*24+hour: sum(item for item in peak_data_rec_list[key])})

    #
    # Media data by weekly hour
    #
    weekly_list = defaultdict(list)
    weekly_res = []
    for d in weekly: # you can list as many input dicts as you want here
        for key, value in d.iteritems():
            weekly_list[key].append(value)
    for key in weekly_list.keys():
        weekly_res.append({'hour':key, 'value' : sum(item for item in weekly_list[key])/ len(weekly_list[key])})
        writer.writerow([datetime.now(), int(self.id), int(self.year), int(key), sum(item for item in weekly_list[key])/ len(weekly_list[key]), 'Eu/MWh'])
    # uploadweekly(streamw)


def upload_budget_med(self, shedule, peak_season, peak_cc_season):
    stream = StringIO.StringIO()
    writer = csv.writer(stream, delimiter='\t')
    streamm = StringIO.StringIO()
    writerm = csv.writer(streamm, delimiter='\t')
    streamw = StringIO.StringIO()
    writerw = csv.writer(streamw, delimiter='\t')
    
    # With defautl riscs
    try:
        meds = (float(sum(item for item in peak_season['summer'])) / float(sum(item for item in peak_cc_season['summer']))) / 10
    except:
        meds = 0
    try:
        medw = (float(sum(item for item in peak_season['winter'])) / float(sum(item for item in peak_cc_season['winter']))) / 10
    except:
        medw = 0
    
    # pwb = RiscRecord.objects.get(risc = Risc.objects.get(name='Risque prix'), year = self.year, pfc=self.pfc).value
    try:
        parameters = ParameterRecord.objects.filter(offer = self.offer, year=int(self.year), parameter=Parameter.objects.get(code='efforts')).aggregate(Sum('value'))
        if parameters['value__sum'] == None:
            pfsum = 0
        else:
            pfsum = parameters['value__sum']
    except:
        pfsum = 0
    # PWB value
    try:
        if self.pfc_market:
            riscsd_data = list(RiscRecord.objects.filter(pfc_market=self.pfc_market,
                                                    year = int(self.year),
                                                    risc = Risc.objects.get(name='Risque PwB')
                                                    ).values_list('value', flat=True))
        else:
            riscsd_data = list(RiscRecord.objects.filter(pfc=self.pfc,
                                                         year=int(self.year),
                                                         risc=Risc.objects.get(name='Risque PwB')
                                                         ).values_list('value', flat=True))

        riscd = 0
        for drisc in riscsd_data:
            riscd += drisc
    except:
        riscd = 0

    # Volume value < 2020
    if self.year < 2020:
        try:
            if self.pfc_market:
                risv = RiscRecord.objects.get(pfc_market=self.pfc_market,
                                        year = int(self.year),
                                        risc = Risc.objects.get(name__icontains='Risque volume')
                                        ).value
            else:
                risv = RiscRecord.objects.get(pfc=self.pfc,
                                              year=int(self.year),
                                              risc=Risc.objects.get(
                                                  name__icontains='Risque volume')
                                              ).value
        except:
            risv = 0
    else:
        risv = 0

    # Prix value
    try:
        if self.pfc_market:
            prix = RiscRecord.objects.get(risc = Risc.objects.get(name='Risque prix'), year = self.year, pfc_market=self.pfc_market)
        else:
            prix = RiscRecord.objects.get(risc = Risc.objects.get(name='Risque prix'), year = self.year, pfc=self.pfc)
            
        if prix:
            if self.offer.validation_time:
                print('offer validation_time exists ')
                prixv = prix.value * sqrt(self.offer.validation_time)
            else:
                print('offer validation_time not exists')
                prixv = prix.value
        else:
            prixv = 0
    
    except:
        prixv = 0
    
    try:
        pvarameters = ParameterRecord.objects.filter(parameter = Parameter.objects.get(code='majors'), offer = self.offer, year=int(self.year)).aggregate(Sum('value'))
        if pvarameters['value__sum'] == None:
            pvsum = 0
        else:
            pvsum = pvarameters['value__sum']
    except:
        pvsum = 0

    # print 'prix == ', prixv
    # print 'summer price ===== ', meds, meds + riscd + prixv + risv + pfsum
    # print 'Winter price ===== ', medw, medw + riscd + prixv + risv + pfsum
    # print 'self.offer.years_liss_list = ', self.offer.lissage, self.offer.years_liss_list
    if self.offer.lissage and (str(self.year) not in self.offer.years_liss_list):
            prev_offers= Offer.objects.filter(cc=self.offer.cc, offer_status='signee', lissage=False).exclude(lis_force=True, lis_manual_expire__lte=datetime.now())
            prev_offer = prev_offers[0]
            # print 'prev_offer =========== ', prev_offer
            try:
                BudgetMedSeasonMajorationRecord = apps.get_model("budget", "BudgetMedSeasonMajorationRecord")
                bg_maj_summer = BudgetMedSeasonMajorationRecord.objects.get(budget__offer=prev_offer, year=self.year, schedule=shedule, season='Summer')
                bg_maj_winter = BudgetMedSeasonMajorationRecord.objects.get(budget__offer=prev_offer,  year=self.year, schedule=shedule, season='Winter')
               # print 'bg_summer, bg_winter == ', bg_summer, bg_winter, (1 - (int(self.offer.percent) / 100))
                writerm.writerow([datetime.now(), int(self.id), 'Summer', shedule.id, int(self.year), bg_maj_summer.value, 'ct/kWh'])
                writerm.writerow([datetime.now(), int(self.id), 'Winter', shedule.id, int(self.year), bg_maj_winter.value, 'ct/kWh'])
            except:
                writerm.writerow([datetime.now(), int(self.id), 'Summer', shedule.id, int(self.year), 0, 'ct/kWh'])
                writerm.writerow([datetime.now(), int(self.id), 'Winter', shedule.id, int(self.year), 0, 'ct/kWh'])

            try:
                BudgetMedSeasonRecord = apps.get_model("budget", "BudgetMedSeasonRecord")
                bg_summer = BudgetMedSeasonRecord.objects.get(budget__offer=prev_offer, year=self.year, schedule=shedule, season='Summer')
                bg_winter = BudgetMedSeasonRecord.objects.get(budget__offer=prev_offer,  year=self.year, schedule=shedule, season='Winter')
                
                # print 'bg_summer, bg_winter == ', bg_summer, bg_winter, (1 - (int(self.offer.percent) / 100))
                writer.writerow([datetime.now(), int(self.id), 'Summer', shedule.id, int(self.year), bg_summer.value, 'ct/kWh'])
                writer.writerow([datetime.now(), int(self.id), 'Winter', shedule.id, int(self.year), bg_winter.value, 'ct/kWh'])
               
            except:
                print 'no med unique'
    else:

        if meds == 0:
            writer.writerow([datetime.now(), int(self.id), 'Summer', shedule.id, int(self.year), meds, 'ct/kWh'])
            writerm.writerow([datetime.now(), int(self.id), 'Summer', shedule.id, int(self.year), meds, 'ct/kWh'])
        else:
            writer.writerow([datetime.now(), int(self.id), 'Summer', shedule.id, int(self.year), meds + riscd + prixv + risv + pfsum, 'ct/kWh'])
            writerm.writerow([datetime.now(), int(self.id), 'Summer', shedule.id, int(self.year), meds + riscd + prixv + risv + pvsum, 'ct/kWh'])
            
        if medw == 0:
            writer.writerow([datetime.now(), int(self.id), 'Winter', shedule.id, int(self.year), medw, 'ct/kWh'])
            writerm.writerow([datetime.now(), int(self.id), 'Winter', shedule.id, int(self.year), medw, 'ct/kWh'])
        else:
            writer.writerow([datetime.now(), int(self.id), 'Winter', shedule.id, int(self.year), medw + riscd + prixv + risv + pfsum, 'ct/kWh'])
            writerm.writerow([datetime.now(), int(self.id), 'Winter', shedule.id, int(self.year), medw + riscd + prixv + risv + pvsum, 'ct/kWh'])

    upload_med_season(stream)
    upload_med_maj_season(streamm)




    # With all riscs and parameters
    parameters = ParameterRecord.objects.filter(offer = self.offer, year=int(self.year)).aggregate(Sum('value'))
    if parameters['value__sum'] == None:
        psum = 0
    else:
        psum = parameters['value__sum']

    try:
        if self.pfc_market:
            riscrv = RiscRecord.objects.get(pfc_market=self.pfc_market,
                                        year = int(self.year),
                                        risc = Risc.objects.get(name__icontains='Risque volume')
                                        ).value
        else:
            riscrv = RiscRecord.objects.get(pfc=self.pfc,
                                            year=int(self.year),
                                            risc=Risc.objects.get(name__icontains='Risque volume')
                                            ).value
    except:
        riscrv = 0

    try:
        risceco = 0
        for ris in Risc.objects.filter(code=self.offer.energy_type):
            try:
                if self.pfc_market:
                    risceco += RiscRecord.objects.get(pfc_market=self.pfc_market,
                                            year = int(self.year),
                                            risc = ris
                                            ).value
                else:
                    risceco += RiscRecord.objects.get(pfc=self.pfc,
                                            year = int(self.year),
                                            risc = ris
                                            ).value
            except:
                risceco += 0
    except:
        risceco = 0
    
    # print 'risceco == ', risceco, self.offer.energy_type,  Risc.objects.filter(code=self.offer.energy_type)

    if self.offer.lissage_years:
        try:
            lis_data = self.offer.lissage_years['lissage_years']['lissage']
            # print lis_data
            for liss in lis_data:
              for key, lis in liss.iteritems():
                if str(key) == str(self.year):
                    lis_value = lis
            # print 'lis budget value == ', lis_value
        except:
            try:
                json_lis_data = ast.literal_eval(self.offer.lissage_years)
                lis_data = json_lis_data['lissage_years']['lissage']
                # print lis_data
                for liss in lis_data:
                    for key, lis in liss.iteritems():
                        if str(key) == str(self.year):
                            lis_value = lis
                # print 'lis budget value == ', lis_value
            except:
                lis_value = 0

    # print 'risvolume == ', riscrv
    # print 'lis value == ', lis_value
    # print 'summer price final ===== ', meds, meds + riscd + prixv + riscrv + psum + lis_value
    # print 'Winter price final ===== ', medw, medw + riscd + prixv + riscrv + psum + lis_value
    # print 'lissage years ==== ', self.offer.lissage and (str(self.year) not in self.offer.years_liss_list)
    if self.offer.lissage and (str(self.year) not in self.offer.years_liss_list):
            prev_offers= Offer.objects.filter(cc=self.offer.cc, offer_status='signee', lissage=False).exclude(lis_force=True, lis_manual_expire__lte=datetime.now())
            prev_offer = prev_offers[0]

            try:
                BudgetMedSeasonWithRiscsRecord = apps.get_model("budget", "BudgetMedSeasonWithRiscsRecord")

                bgf_summer = BudgetMedSeasonWithRiscsRecord.objects.get(budget__offer=prev_offer, year=self.year, schedule=shedule, season='Summer')
                bgf_winter = BudgetMedSeasonWithRiscsRecord.objects.get(budget__offer=prev_offer, year=self.year, schedule=shedule, season='Winter')
                # print 'bgf_summer, bgf_winter == ', bgf_summer, bgf_winter
                writerw.writerow([datetime.now(), int(self.id), 'Summer', shedule.id, int(self.year), bgf_summer.value * (1 + (float(self.offer.percent) / 100)), 'ct/kWh'])
                writerw.writerow([datetime.now(), int(self.id), 'Winter', shedule.id, int(self.year), bgf_winter.value * (1 + (float(self.offer.percent) / 100)), 'ct/kWh'])
            except:
                print 'no med unique'
    else:
        if meds == 0:
            writerw.writerow([datetime.now(), int(self.id), 'Summer', shedule.id, int(self.year), meds, 'ct/kWh'])
        else:
            writerw.writerow([datetime.now(), int(self.id), 'Summer', shedule.id, int(self.year), meds + riscd + prixv + riscrv + psum + lis_value + risceco, 'ct/kWh'])
        
        if medw == 0:
            writerw.writerow([datetime.now(), int(self.id), 'Winter', shedule.id, int(self.year), medw, 'ct/kWh'])
        else:
            writerw.writerow([datetime.now(), int(self.id), 'Winter', shedule.id, int(self.year), medw + riscd + prixv + riscrv + psum + lis_value + risceco, 'ct/kWh'])
            

    upload_med_risc_season(streamw)
    # except:
    #     print 'Error on obtaining the prices'


def weekly_headge(self, shedule, rec_list):
    weekly_headge = defaultdict(list)
    peak_data_rec_list = defaultdict(list)
    for d in rec_list: # you can list as many input dicts as you want here
        for key, value in d.iteritems():
            peak_data_rec_list[key].append(value)

    for key in peak_data_rec_list.keys():
        # weekday = int(datetime.strptime(key[:10], '%Y-%m-%d').isoweekday())
        weekly_headge[key].append(max(item for item in peak_data_rec_list[key]))

    weekly_med_headge = []
    for key in weekly_headge.keys():
        # print {'day':key, 'shedule': shedule, 'year':self.year , 'value': max(item for item in weekly_headge[key])}
        weekly_med_headge.append(max(item for item in weekly_headge[key]))
    # print 'shedule', shedule, 'headge value = ', sum(weekly_med_headge) / len(weekly_med_headge)
