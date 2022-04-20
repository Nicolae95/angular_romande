from rest_framework import serializers
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.utils import timezone
from companies.models import Meter, Site, Company
from django.http import HttpRequest
from django_countries.fields import CountryField
from datetime import datetime, timedelta, time
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from math import sqrt
import csv
import json
import ast
import pytz
import StringIO
import io
import copy
from django.db.models import Sum, F, Q
from django.core.files.images import ImageFile
from .models import *
from pfc.serializers import *
from translations.models import *
from type.serializers import *
from typepondere.serializers import *
from core.serializers import *
from pfc.serializers import *
from core.models import *
from companies.serializers import *
from budget.models import *
from cockpit.models import *
from type.models import *
from typepondere.models import *
from core.logic.db.upload import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
from utils.send_mail import py_mail
from collections import defaultdict


class DateTimeFieldUTC(serializers.DateTimeField):
    '''Class to make output of a DateTime Field timezone aware
    '''
    def to_representation(self, value):
        cet = pytz.timezone('UTC')
        # value = cet.localize(value)
        interval_cc = pytz.utc.localize(datetime.strptime(str(value)[:16], '%Y-%m-%d %H:%M'))
        value = interval_cc.astimezone(pytz.timezone('CET'))

        return super(DateTimeFieldUTC, self).to_representation(str(value))


class DateTimeFieldCET(serializers.DateTimeField):
    '''Class to make output of a DateTime Field timezone aware
    '''

    def to_representation(self, value):
        cet = pytz.timezone('UTC')
        # value = cet.localize(value)
        interval_cc = pytz.utc.localize(datetime.strptime(str(value)[:16], '%Y-%m-%d %H:%M'))
        value = interval_cc.astimezone(pytz.timezone('CET'))
        expiration_date = value.strftime('%d/%m/%Y %H:%M')
        # return super(DateTimeFieldUTC, self).to_representation(str(value))
        return super(DateTimeFieldCET, self).to_representation(expiration_date)


def signature(validated_data, temp, offer):
    if validated_data['lis_years']:
        years = validated_data['lis_years']
    else:
        years = validated_data['years']
    if years:
        years = years.split(',')


    records = EnergyConsumptionRecord.objects.filter(meter=validated_data['cc']).aggregate(Sum('value'))
    
    # print 'volume for molumetrie ======== ', int(round(records['value__sum']))
    if years != ['']:
        volume = (int(round(records['value__sum'])) / float(10**6)) * len(years)

    years = map(lambda x: int(x), years)
    majors = []
    for key in temp['majors'].keys():
        if key != '':
            if int(key) in years:
                majors.append(temp['majors'][key])
    if validated_data['pfc_market']:
        bgs = Budget.objects.filter(offer=offer, pfc_market=validated_data['pfc_market']).values_list('id', flat=True)
    else:
        bgs = Budget.objects.filter(offer=offer, pfc=validated_data['pfc']).values_list('id', flat=True)
        
    budgets = list(BudgetAverageWithoutEfort.objects.filter(year__in=years, budget__in=bgs).values_list('value', flat=True))
    # print 'budgets = ', budgets, len(budgets)
    # print 'sum(majors) = ', majors, sum(majors), len(majors)
    major_med = sum(majors)/len(majors)
    prix_med = sum(budgets)/len(budgets)
    maj = ((major_med + prix_med)/ prix_med) * 100
    print('maj ======== ', maj)
    print('volume ======= ', volume)
    q = Q()
    fonction = 3
    if maj < 100 and volume < 30:
        fonction = 5
        q = Q(fonction=5)
    elif maj < 100 and volume >= 30: #CEO
        fonction = 9
        q = Q(fonction=9)
    elif maj >= 100 and maj < 102 and volume < 20:  # Resp. Marche
        fonction = 4
        q = Q(fonction=4)
    elif maj >= 100 and maj < 102 and volume >= 20 and volume < 100:
        fonction = 5
        q = Q(fonction=5)
    elif maj >= 100 and maj < 102 and volume >= 100:  # CEO
        fonction = 9
        q = Q(fonction=9)
    elif maj >= 102 and volume < 12:  # 
        fonction = 3
        q = Q(fonction=3)
        offer.offer_status = 'indicative'
        offer.lis_force = False
        try:
            sign = User.objects.get(email='yves.bonaccorsi@romande-energie.ch')
            offer.signer = sign
        except:
            try:
                sign = Profile.objects.filter(fonction=3)[0]
                offer.signer = sign.user
            except:
                print('no status 3')
    elif maj >= 102 and volume >= 12 and volume < 20:  #
        fonction = 4
        q = Q(fonction=4)
    elif maj >= 102 and volume >= 20 and volume < 100:  #
        fonction = 5
        q = Q(fonction=5)
    elif maj >= 102 and volume >= 100:  #
        fonction = 9
        q = Q(fonction=9)
    profiles = Profile.objects.filter(q)
    print(profiles)
    users = [profile.user for profile in profiles]
    offer.marge = maj
    offer.volumetrie = volume
    offer.fonction = fonction
    offer.signatures.clear()
    offer.signatures.add(*users)
    offer.save()


def generate_cc_budgets(self, validated_data, obj, bcreate=True):
    cet = pytz.timezone('UTC')
    print 'validated_data function = ', validated_data['pfc']
    meds = []
    days = []
    data_year = int(validated_data['cc'].site.year)
    transaction_years = map(lambda x: data_year + x, range(1,7))

    if validated_data['pfc_market']:
        if validated_data['pfc_market'].risc:
            obj.risc = validated_data['pfc_market'].risc
        if validated_data['pfc_market'].eco:
            obj.eco = validated_data['pfc_market'].eco
        obj.save()
    else:
        if validated_data['pfc'].risc:
            obj.risc = validated_data['pfc'].risc
        if validated_data['pfc'].eco:
            obj.eco = validated_data['pfc'].eco
        obj.save()

    if validated_data['lissage_years']:
        try:
            lis_offer = validated_data['lissage_years']['lissage_years']['offer']
            obj.lissage_base = int(lis_offer)
            obj.save()
            lioffer = Offer.objects.get(id=int(lis_offer))
            lioffer.status_lisse = True
            if obj.offer_type == 'SME':
                # interval_date_fin = pytz.utc.localize(datetime.strptime(str(obj.date_fin)[:16], '%Y-%m-%d %H:%M'))
                # value = interval_date_fin.astimezone(pytz.timezone('CET'))
                lioffer.lis_manual_expire = obj.date_fin
            lioffer.save()
            # print 'lis budget value == ', lis_value
        except:
            try:
                json_is_offer = ast.literal_eval(str(validated_data['lissage_years']))
                is_offer = json_is_offer['lissage_years']['offer']
                obj.lissage_base = int(lis_offer)
                obj.save()
                lioffer = Offer.objects.get(id=int(lis_offer))
                lioffer.status_lisse = True
                if obj.offer_type == 'SME':
                    # interval_date_fin = pytz.utc.localize(datetime.strptime(str(obj.date_fin)[:16], '%Y-%m-%d %H:%M'))
                    # value = interval_date_fin.astimezone(pytz.timezone('CET'))
                    lioffer.lis_manual_expire = obj.date_fin
                lioffer.save()
            except:
                lis_offer = None

    for year in obj.years.split(','):
        if obj.pfc_date_first:
            fdate = make_naive(obj.pfc_date_first, pytz.timezone('CET'))
            if fdate.year == int(year):
                cet_cc_from = cet.localize(datetime(int(year), fdate.month, fdate.day, 0, 0), is_dst=None)
            else:
                cet_cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        else:
            cet_cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)

        if obj.pfc_date_last:
            ldate = make_naive(obj.pfc_date_last, pytz.timezone('CET'))
            if ldate.year == int(year):
                cet_cc_to = cet.localize(datetime(int(year), ldate.month, ldate.day, 23, 59), is_dst=None)
            else:
                cet_cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        else:
            cet_cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)

        # cet_cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        # cet_cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        
        print 'cc == ', validated_data['cc']
        liss = False
        lis_value = 0

        print('validated_data lissage_years === ', validated_data['lissage_years'], type(validated_data['lissage_years']))
        print('validated_data percent === ', validated_data['percent'], type(validated_data['percent']))

        if validated_data['lissage_years']:
            try:
                lis_data = validated_data['lissage_years']['lissage_years']['lissage']
                print 'liss dataaa = ', lis_data
                liss = True
                for lissag in lis_data:
                  for key, lis in lissag.iteritems():
                    print 'lisasage key and value === ', key, lis
                    if str(key) == str(year):
                        lis_value = lis
                        print 'lisassssage value ==== ', lis_value, lis
                # print 'lis budget value == ', lis_value
            except:
                try:
                    lis_json = ast.literal_eval(str(validated_data['lissage_years']))
                    lis_data = lis_json['lissage_years']['lissage']
                    print 'liss dataaa = ', lis_data
                    liss = True
                    for lissag in lis_data:
                        for key, lis in lissag.iteritems():
                            print 'lisasage key and value === ', key, lis
                            if str(key) == str(year):
                                lis_value = lis
                                print 'lisassssage value ==== ', lis_value, lis
                    # print 'lis budget value == ', lis_value
                except:
                    lis_value = 0
        
        if bcreate == False:
            budget = Budget.objects.get(year=int(year),
                                           offer=obj,
                                           pfc=validated_data['pfc'],
                                           pfc_market=validated_data['pfc_market'],
                                           cc=validated_data['cc'],
                                           unit=validated_data['unit'],
                                           lissage=liss
                                           )
        else:
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
            if validated_data['pfc_market']:
                prix = RiscRecord.objects.get(risc = Risc.objects.get(name='Risque prix'), year = int(year), pfc_market=validated_data['pfc_market']).value
            else:
                prix = RiscRecord.objects.get(risc = Risc.objects.get(name='Risque prix'), year = int(year), pfc=validated_data['pfc']).value
        except:
            prix = 0

        print 'prixv ===== ', prix
        try:
            prixv = prix * sqrt(int(validated_data['validation_time']))
            print 'prix rad', prixv
        except:
            prixv = prix
            print 'prix wihout radical rad', prixv
        

        try:
            if validated_data['pfc_market']:
                risc_record = RiscRecord.objects.filter(risc = Risc.objects.get(name='Risque PwB'),  pfc_market = validated_data['pfc_market'], year=int(year)).aggregate(Sum('value'))
            else:
                risc_record = RiscRecord.objects.filter(risc = Risc.objects.get(name='Risque PwB'),  pfc = validated_data['pfc'], year=int(year)).aggregate(Sum('value'))
            if risc_record['value__sum'] == None:
                rsum = 0
            else:
                rsum = risc_record['value__sum']
        except:
            rsum = 0

        try:
            if validated_data['pfc_market']:
                risv = RiscRecord.objects.get(pfc_market=validated_data['pfc_market'],
                                            year = int(year),
                                            risc = Risc.objects.get(name__icontains='Risque volume')
                                            ).value
            else:
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
            risceco = 0
            for ris in Risc.objects.filter(code=obj.energy_type):
                try:
                    if validated_data['pfc_market']:
                        risceco += RiscRecord.objects.get(pfc_market=validated_data['pfc_market'],
                                            year = int(year),
                                            risc = ris
                                            ).value
                    else:
                        risceco += RiscRecord.objects.get(pfc=validated_data['pfc'],
                                                              year=int(year),
                                                              risc=ris
                                                              ).value
                except:
                    risceco += 0
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
        
        try:
            pvarameters = ParameterRecord.objects.filter(offer = obj, year=int(year), parameter=Parameter.objects.get(code='majors')).aggregate(Sum('value'))
            if pvarameters['value__sum'] == None:
                pvsum = 0
            else:
                pvsum = pvarameters['value__sum']
        except:
            pvsum = 0

        print 'lisssssssssssss value === ', lis_value
        print 'values price first table = ', ((bsum/float(vsum)) / float(10.0)) + prixv + rsum + riscvf + pfsum
        print 'offer lissage == ', obj.lissage, str(year), obj.years_liss_list, obj.lissage

        if bcreate == False:
            if len(obj.shedules.all()) == 1:
                shedules = Shedule.objects.filter(id__in=[1,2])
            else:
                shedules = obj.shedules.all()
            for shedule in shedules:
                bg_summer = BudgetMedSeasonRecord.objects.get(budget=budget, year=int(year), schedule=shedule, season='Summer')
                bg_winter = BudgetMedSeasonRecord.objects.get(budget=budget, year=int(year), schedule=shedule, season='Winter')

                bg_maj_summer = BudgetMedSeasonMajorationRecord.objects.get(budget=budget, year=int(year), schedule=shedule, season='Summer')
                bg_maj_summer.value = bg_summer.value + pvsum
                bg_maj_summer.save()
                bg_maj_winter = BudgetMedSeasonMajorationRecord.objects.get(budget=budget, year=int(year), schedule=shedule, season='Winter')
                bg_maj_winter.value = bg_winter.value + pvsum
                bg_maj_winter.save()

                bgf_summer = BudgetMedSeasonWithRiscsRecord.objects.get(budget=budget, year=int(year), schedule=shedule, season='Summer')
                if int(year) > 2019:
                    bgf_summer.value = bg_summer.value + risv + psum + lis_value + risceco
                else:
                    bgf_summer.value = bg_summer.value + psum + lis_value + risceco
                bgf_summer.save()
                bgf_winter = BudgetMedSeasonWithRiscsRecord.objects.get(budget=budget, year=int(year), schedule=shedule, season='Winter')
                if int(year) > 2019:
                    bgf_winter.value = bg_winter.value + risv + riscvs + psum + lis_value + risceco
                else:
                    bgf_winter.value = bg_winter.value + riscvs + psum + lis_value + risceco
                bgf_winter.save()
            
            try:
                bgc = BudgetAverageClean.objects.get(year=int(year), budget=budget)
                bgc.value = ((bsum/float(vsum)) / float(10.0))
                bgc.save()
            except:
                print('no budget clean')
            try:
                bge = BudgetAverageWithoutEfort.objects.get(year=int(year), budget=budget)
                bge.value = ((bsum/float(vsum)) / float(10.0)) + prixv + rsum + riscvf
                bge.save()
            except:
                print('no budget wf')
            try:
                bgm = BudgetAverageMajorationPerYear.objects.create(year=int(year), value=0, budget=budget)
                bgm.value = ((bsum/float(vsum)) / float(10.0)) + prixv + rsum + riscvf + pvsum
                bgm.save()
            except:
                print('no budget mj')
            bga = BudgetAveragePerYear.objects.get(year=int(year), budget=budget)
            bga.value = ((bsum/float(vsum)) / float(10.0)) + prixv + rsum + riscvf + pfsum
            bga.save()
            bgr = BudgetAveragePerYearRiscs.objects.get(year=int(year), budget=budget)
            bgr.value=((bsum/ float(vsum)) / float(10.0)) + prixv + rsum + riscvf + psum + lis_value + riscvs + risceco
            bgr.save()
        else:
            if obj.lissage and (str(year) not in obj.years_liss_list):
                prev_offers = Offer.objects.filter(cc=obj.cc, offer_status='signee', lissage=False).exclude(lis_force=True, lis_manual_expire__lte=datetime.now())
                prev_offer = prev_offers[0]
                print 'prev offer =========== ', validated_data['percent'], (1 + (float(validated_data['percent']) / 100)), prev_offer
                try:
                    bgc = BudgetAverageClean.objects.get(year=int(year), budget__offer=prev_offer)
                except:
                    bgc = BudgetAveragePerYear.objects.get(year=int(year), budget__offer=prev_offer)
                bge = BudgetAverageWithoutEfort.objects.get(year=int(year), budget__offer=prev_offer)
                bga = BudgetAveragePerYear.objects.get(year=int(year), budget__offer=prev_offer)
                bgr = BudgetAveragePerYearRiscs.objects.get(year=int(year), budget__offer=prev_offer)
                
                try:
                    bgm = BudgetAverageMajorationPerYear.objects.get(year=int(year), budget__offer=prev_offer)
                    BudgetAverageMajorationPerYear.objects.create(year=int(year), value=bgm.value, budget=budget)
                except:
                    BudgetAverageMajorationPerYear.objects.create(year=int(year), value=0, budget=budget)

                try:
                    BudgetAverageClean.objects.create(year=int(year), value=bgc.value, budget=budget)
                except:
                    print('no budget clean')
                BudgetAverageWithoutEfort.objects.create(year=int(year), value=bge.value, budget=budget)
                BudgetAveragePerYear.objects.create(year=int(year), value=bga.value, budget=budget)
                print('value of the bgr.value =========== ', bgr.value, float(bgr.value) * (1 + (float(validated_data['percent']) / 100)))
                BudgetAveragePerYearRiscs.objects.create(year=int(year), value=(float(bgr.value) * (1 + (float(validated_data['percent']) / 100))), budget=budget)
            else:
                BudgetAverageClean.objects.create(year=int(year), value=((bsum/float(vsum)) / float(10.0)), budget=budget)
                BudgetAverageWithoutEfort.objects.create(year=int(year), value=((bsum/float(vsum)) / float(10.0)) + prixv + rsum + riscvf, budget=budget)
                BudgetAveragePerYear.objects.create(year=int(year), value=((bsum/float(vsum)) / float(10.0)) + prixv + rsum + riscvf + pfsum, budget=budget)
                BudgetAverageMajorationPerYear.objects.create(year=int(year), value=((bsum/float(vsum)) / float(10.0)) + prixv + rsum + riscvf + pvsum, budget=budget)
                BudgetAveragePerYearRiscs.objects.create(year=int(year), value=((bsum/ float(vsum)) / float(10.0)) + prixv + rsum + riscvf + psum + lis_value + riscvs + risceco, budget=budget)


class OfferStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferStop
        fields = ('id', 'stop',)


class GRDSerializer(serializers.ModelSerializer):
    class Meta:
        model = GRD
        fields = ('id', 'name',)


class ConstantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Constants
        fields = ('id', 'name', 'value')


class RiscSerializer(serializers.ModelSerializer):
    class Meta:
        model = Risc
        fields = ('id', 'name', )


class RiscRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiscRecord
        fields = ('id', 'risc', 'value', 'unit', 'year')


class OfferEditCockpitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ('id', 'cockpit', )


class OfferEditStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ('id', 'offer_status', )


class OfferEditNameSerializer(serializers.ModelSerializer):
    majors = serializers.JSONField()
    sur_go = serializers.JSONField()
    
    class Meta:
        model = Offer
        fields = ('id', 'name', 'majors', 'energy_type', 'sur_go')
        # fields = ('id', 'name', 'majors')
    
    def update(self, instance, validated_data):
        majors = defaultdict()
        sur_go = defaultdict()
        mparameters = ParameterRecord.objects.filter(offer = instance, parameter=Parameter.objects.get(code='majors'))
        mparameters.delete()
        sparameters = ParameterRecord.objects.filter(offer = instance, parameter=Parameter.objects.get(code='sur_go'))
        sparameters.delete()
        nam = validated_data['name']
        for mp in validated_data['majors']:
            majors[mp['year']] = mp['value']
            mj = ParameterRecord(offer=instance, year=int(mp['year']), value=float(mp['value']), parameter=Parameter.objects.get(code='majors'))
            mj.save()
        for mp in validated_data['sur_go']:
            sur_go[mp['year']] = mp['value']
            msg = ParameterRecord(offer=instance, year=int(mp['year']), value=float(mp['value']), parameter=Parameter.objects.get(code='sur_go'))
            msg.save()
        validated_data['sur_go'] = sur_go
        validated_data['majors'] = majors
        validated_data['name'] = instance.name
        validated_data['cc'] = instance.cc
        validated_data['pfc'] = instance.pfc
        validated_data['pfc_market'] = instance.pfc_market
        validated_data['unit'] = instance.unit
        validated_data['lissage_years'] = instance.lissage_years
        validated_data['percent'] = instance.percent
        validated_data['lis_years'] = instance.lis_years
        validated_data['validation_time'] = instance.validation_time
        validated_data['validation_time'] = instance.validation_time
        validated_data['years'] = instance.years
        temp = copy.copy(validated_data)
        instance.energy_type = validated_data['energy_type']
        instance.save()
        generate_cc_budgets(self, validated_data, instance, False)
        instance.offer_status = 'confirmer'
        signature(validated_data, temp, instance)
        instance.updated = datetime.now()
        instance.name = nam
        instance.save()
        return instance


class OfferTiagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ('emp_id', 'name', 'nr_opportunite', 'created', 'updated', 'signee_date', 'type', 'status', 'id_lissee', 'meters', 'years_signee', 'prix_resa_rec', 'prix_vente_hors_go_produitservice', 'prix_vente_final',
                  'prix_resa_rec_hp_hc', 'prix_vente_hors_go_produitservice_hp_hc', 'prix_vente_final_hp_hc', 'ID_PFC_ajustee', 'ID_primes_risques', 'ID_garanties_origine')


class OfferExternSerializer(serializers.ModelSerializer):
    client = CompanyExternSerializer(source='company')
    grd = GRDSerializer()
    meters = serializers.JSONField(read_only=True)

    class Meta:
        model = Offer
        fields = ('emp_id', 'name', 'created', 'updated', 'expiration_date', 'nr_opportunite', 'type', 'status', 'hp_hc', 'years_list', 'pfc_data', 'admin_data', 'client',
                  'grd', 'meters', 'comment', 'cockpit', 'lissage', 'expiration_date', 'signed_file', 'unsigned_file', 'eligibilite',)



class OfferEditPfcMarketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer
        fields = ('id', 'pfc_market', 'fonction', 'volumetrie', 'marge')
        read_only_fields = ('id', 'fonction', 'volumetrie', 'marge')

    # pfc_market = serializers.PrimaryKeyRelatedField(read_only=True)
    # energies = serializers.JSONField()
    # majors = serializers.JSONField(required=False)
    # efforts = serializers.JSONField(required=False)
    # ps1 = serializers.JSONField(required=False)
    # ps2 = serializers.JSONField(required=False)
    # sur_go = serializers.JSONField(required=False)

    # class Meta:
    #     model = Offer
    #     fields = ('id', 'pfc_market', 'energy_type', 'efforts', 'majors',
    #               'ps1', 'ps2', 'sur_go', 'fonction', 'volumetrie', 'marge')
    #     read_only_fields = ('id', 'fonction', 'volumetrie', 'marge')

    # def del_parameters(self, validated_data):
    #     values = ['efforts', 'sur_go', 'majors', 'ps1', 'ps2']
    #     for name in values:
    #         # print 'dell', name, validated_data[name]
    #         validated_data.pop(name, None)
    #     return validated_data

    # def create_parameters(self, validated_data, offer):
    #     # values = ['decotes', 'efforts', 'energies', 'majors', 'ps1', 'ps2']
    #     values = ['efforts', 'sur_go', 'majors', 'ps1', 'ps2']
    #     for name in values:
    #         for key in validated_data[name].keys():
    #             ParameterRecord.objects.create(offer=offer,  year = key, value = validated_data[name][key], parameter = Parameter.objects.get(code=name))

    def update(self, instance, validated_data):
        print('validated data=', validated_data)
        cet = pytz.timezone('UTC')
        majors = defaultdict()
        mparameters = ParameterRecord.objects.filter(offer = instance, parameter=Parameter.objects.get(code='majors')).values('value', 'year')
        for mp in mparameters:
            majors[mp['year']] = mp['value']
        validated_data['majors'] = majors
        temp = copy.copy(validated_data)
        # validated_data = self.del_parameters(validated_data)
        # self.create_parameters(temp, instance)
        instance.pfc_market = validated_data.get('pfc_market', instance.pfc_market)
        instance.energy_type = validated_data.get('energy_type', instance.energy_type)
        instance.offer_status = 'confirmer'
        validated_data['name'] = instance.name
        validated_data['cc'] = instance.cc
        validated_data['pfc'] = instance.pfc
        validated_data['unit'] = instance.unit
        validated_data['lis_years'] = instance.lis_years
        validated_data['lissage_years'] = instance.lissage_years
        validated_data['years'] = instance.years
        validated_data['percent'] = instance.percent
        validated_data['validation_time'] = instance.validation_time
        generate_cc_budgets(self, validated_data, instance)
        signature(validated_data, temp, instance)
        instance.updated = datetime.now()
        instance.save()
        return instance


class OfferEditEnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ('id', 'energy_type', )



class OfferSerializer(serializers.ModelSerializer):
    meters = serializers.JSONField(read_only=True)
    # expiration_date = DateTimeFieldUTC(read_only=True)

    class Meta:
        model = Offer
        fields = ('id', 'emp_id', 'name', 'unique_id', 'company', 'consumption', 'datetime_from', 'datetime_to', 'profile_pondere', 'employees', 'pfc',
                  'pfc_market', 'profile', 'cc', 'years', 'unit', 'offer_type', 'riscs', 'shedules', 'validation_time', 'meters', 'expiration_date',
                  'offer_status', 'cockpit', 'second_type', 'user', 'lissage', 'mail_date', 'comment', 'nr_opportunite', 'marche', 'releve',
                  'date_debut', 'date_fin', 'energy_type', 'volumetrie', 'marge')


class OfferMetersSerializer(serializers.ModelSerializer):
    meters = serializers.JSONField(read_only=True)
    # expiration_date = DateTimeFieldUTC(read_only=True)
    date_debut = DateTimeFieldCET()
    date_fin = DateTimeFieldCET()
    expiration_date = DateTimeFieldCET()

    class Meta:
        model = Offer
        fields = ('id', 'emp_id', 'unique_id', 'created', 'name', 'company', 'consumption', 'employees', 'pfc', 'pfc_market', 'profile', 'profile_pondere', 'status_lisse',
                  'cc', 'years', 'unit', 'offer_type', 'riscs', 'shedules', 'validation_time', 'meters', 'expiration_date', 'offer_status',
                  'cockpit', 'second_type', 'user', 'signed_file', 'lissage', 'unsigned_file', 'mail_date', 'eligibilite', 'marche', 'releve', 
                  'date_debut', 'date_fin', 'nr_opportunite', 'emails_list', 'entreprise', 'contact', 'surname', 'grd', 'fonction', 'cockpit_data', 'energy_type', 'admin_data',
                  'name_unsigned', 'name_signed', 'name_eligib', 'duree', 'comment', 'grd_name', 'years_liss_list')
        read_only_fields = ('id', 'mail_date', 'lissage', 'emails_list', 'energy_type',
                            'entreprise', 'contact', 'fonction', 'cockpit_data', 'status_lisse', 'duree')


class OfferEditSerializer(serializers.ModelSerializer):
    lissage_years = serializers.JSONField()
    decotes = serializers.JSONField()
    efforts = serializers.JSONField()
    energies = serializers.JSONField()
    majors = serializers.JSONField()
    ps1 = serializers.JSONField()
    ps2 = serializers.JSONField()
    sur_go = serializers.JSONField()
    sme_status = serializers.CharField(required=False)

    class Meta:
        model = Offer
        fields = ('id', 'created', 'name', 'company', 'consumption', 'employees', 'pfc', 'pfc_market', 'profile', 'lissage', 'cc', 'years', 'unit',
                  'offer_type', 'riscs', 'shedules', 'validation_time', 'offer_status', 'sme_status', 'expiration_date', 'cockpit', 'lissage_years', 'decotes', 'efforts',
                  'energies', 'majors', 'ps1', 'ps2', 'second_type', 'user', 'conseiller', 'signed_file', 'unsigned_file', 'eligibilite', 'marche', 'energy_type', 'comment',
                  'nr_opportunite', 'sur_go', 'grd', 'releve', 'date_debut', 'date_fin', 'signatures', 'fonction', 'lis_years', 'percent', 'volumetrie', 'marge',
                  'pfc_date_first', 'pfc_date_last')
        
        read_only_fields = ('id', 'created', 'expiration_date', 'cockpit',
                            'signed_file', 'unsigned_file', 'signatures', 'fonction', 'volumetrie', 'marge')
        extra_kwargs = {'conseiller': {'required': False} }

    def del_parameters(self, validated_data):
        values = ['decotes', 'efforts', 'sur_go', 'energies', 'majors', 'ps1', 'ps2']
        for name in values:
            validated_data.pop(name, None)
        return validated_data

    def create_parameters(self, validated_data, offer):
        values = ['decotes', 'efforts', 'sur_go', 'majors', 'ps1', 'ps2']
        for name in values:
            # print validated_data[name]
            for key in validated_data[name].keys():
                if key != '':
                    ParameterRecord.objects.create(offer=offer,  year = key, value = validated_data[name][key], parameter = Parameter.objects.get(code=name))

    def generate_email_content(self, obj):
        budgets = Budget.objects.filter(offer_id=obj.id, pfc=obj.pfc).values_list('id', flat=True)
        years = Budget.objects.filter(offer_id=obj.id, pfc=obj.pfc).values_list('year', flat=True)
        years = sorted(reduce(lambda r, v: v in r and r or r + [v], years, []))
        budget_season = BudgetMedSeasonRecord.objects.filter(budget__in=budgets,
                                                             year__in=years).annotate(hp_hc=F('schedule__title')).values('year', 'value', 'season', 'hp_hc')
        average_year_price = BudgetAveragePerYear.objects.filter(budget__in=budgets, year__in=years).values('year', 'value')
        print 'season email data === ', list(budget_season)
        context = {
                    "budget_season": list(budget_season),
                    "prices": list(average_year_price),
                    "years":years,
                    "customer": obj.company.name,
                    "surname": obj.company.surname,
                    "offer": obj.id
                  }
        template = get_template('tool/mail/email.html')
        email_content = template.render(context)
        return email_content

    def plot_offer(self, validated_data):
        print validated_data
        # meds.append(bgrecord['value__sum'] / crecord['value__sum'])
        # days.append(validated_data['pfc'].pfc_id)
        # print meds
        # print days
        # figure = io.BytesIO()
        # plt.plot(days, meds)
        # plt.savefig(figure, format="png")
        # data = ImageFile(figure)
        # plot = OfferPlot(offer = obj)
        # plot.figure.save(
        #     name='{}.png'.format(str(obj.id)),
        #     content=data,
        #     save=False
        # )
        # plot.save()

    def expiration_date(self, validated_data):
        date = datetime.now()
        # if int(validated_data['validation_time']) == 1:
        #     expiration_date = datetime.utcnow() + timedelta(days=1)
        expiration_date = datetime.now() + timedelta(days=int(validated_data['validation_time']))
        list_days = [date + timedelta(days=x) for x in range((expiration_date-date).days)]
        try:
            holidays = Location.objects.all()[0].holidays.all().values_list('date', flat=True)
            print holidays
        except:
            holidays = []
        weekend = 0
        for day in list_days:
            if day.isoweekday() > 5:
                weekend = weekend + 1
            else:
                if day in holidays:
                    weekend = weekend + 1
        print 'weekend ========= ', weekend
        if int(validated_data['validation_time']) > 0:
            exp = datetime.now() + timedelta(days=int(validated_data['validation_time'])-1 + weekend)
        else:
            exp = datetime.now() + timedelta(days=weekend)
        print 'exp ======= ', exp, 8-exp.isoweekday()
        if exp.isoweekday() > 5:
            return exp.replace(hour=23, minute=59) + timedelta(days=8-exp.isoweekday())
        else:
            return exp.replace(hour=23, minute=59)


    def create(self, validated_data):
        start = time.time()
        cet = pytz.timezone('UTC')
        temp = copy.copy(validated_data)
        riscs = validated_data['riscs']
        shedules = validated_data['shedules']
        if validated_data['validation_time'] != None:
            validated_data['expiration_date'] = self.expiration_date(validated_data)
        del validated_data['riscs']
        del validated_data['shedules']
        validated_data = self.del_parameters(validated_data)
        obj = Offer.objects.create(**validated_data)
        self.create_parameters(temp, obj)
        obj.riscs.add(*riscs)
        obj.shedules.add(*shedules)
        if validated_data['second_type'] == 'prolongation':
            obj.grd = None
            obj.save()
        if validated_data['offer_type'] == 'SME':
            obj.sme_status = validated_data['offer_status']
            obj.offer_status = 'pending'
            obj.expiration_date = obj.date_fin
            obj.save()
            return obj
        obj.lis_force = True
        obj.offer_status = 'confirmer'
        obj.save()
        stream = StringIO.StringIO()
        writer = csv.writer(stream, delimiter='\t')
        if validated_data['profile'] and validated_data['cc'] == None:
            # print 'True', validated_data['profile'] , validated_data['cc']
            cc = Meter.objects.create(company = validated_data['company'], meter_id = validated_data['name'])
            pt_records = ProfileTypeConsumptionRecord.objects.filter(profile = validated_data['profile'])
            for precord in pt_records:
                # print precord.interval_start, precord.value * validated_data['consumption']
                writer.writerow([datetime.now(), datetime.now(), 106,  cc.id, precord.value * validated_data['consumption'], precord.interval_start, timedelta(hours=1), 'kWh'])
            upload_db(stream)
            trans = Translation(cc = cc)
            trans.save()
            trans.upload_meter()
            for year in obj.years.split(','):
                cet_cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
                cet_cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
                print year
                liss = False
                lis_value = 0
                if validated_data['lissage_years']:
                    try:
                        lissages = validated_data['lissage_years']['lissage_years']['lissage']
                        liss = True
                        for lissage in lissages:
                          for key, lis in lissage.iteritems():
                            if str(key) == str(year):
                                lis_value = lis
                        print 'lis value == ', lis_value
                    except:
                        try:
                            json_lisss = ast.literal_eval(validated_data['lissage_years'])
                            lissages = json_lisss['lissage_years']['lissage']
                            liss = True
                            for lissage in lissages:
                                for key, lis in lissage.iteritems():
                                    if str(key) == str(year):
                                        lis_value = lis
                            print 'lis value == ', lis_value
                        except:
                            lissages = []
                budget = Budget.objects.create(year = int(year),
                                               budget_id = validated_data['name'],
                                               offer = obj,
                                               pfc = validated_data['pfc'],
                                               pfc_market = validated_data['pfc_market'],
                                               cc = cc,
                                               unit = validated_data['unit'],
                                               lissage = liss
                                               )
                budget.produce_report()
                bgrecord = BudgetRecord.objects.filter(budget = budget).aggregate(Sum('value'))
                if year in transaction_years:
                    crecord = TranslationRecord.objects.filter(meter = cc,
                                                               interval_start__gte=cet_cc_from,
                                                               interval_start__lte=cet_cc_to
                                                               ).aggregate(Sum('value'))
                else :
                    crecord = EnergyConsumptionRecord.objects.filter(meter = cc,
                                                                     interval_start__gte=cet_cc_from,
                                                                     interval_start__lte=cet_cc_to
                                                                     ).aggregate(Sum('value'))
                constants = Constants.objects.all().aggregate(Sum('value'))
                if constants['value__sum'] == None:
                    csum = 0
                else:
                    csum = constants['value__sum']
                parameters = ParameterRecord.objects.filter(offer = obj, year=int(year)).aggregate(Sum('value'))

                try:
                    prix = RiscRecord.objects.get(risc = Risc.objects.get(name='Risque prix'), year = int(year), pfc=validated_data['pfc'])
                    if prix:
                        if validated_data['validation_time']:
                            prixv = prix.value * sqrt(int(validated_data['validation_time']))
                            print 'prix rad', prixv
                        else:
                            prixv = prix.value
                            print 'prix not validation_time rad', prixv
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
                BudgetAverageWithoutEfort.objects.create(year=int(year), value=((bsum/float(vsum)) / float(10.0)) + prixv + rsum + riscvf, budget=budget)
                BudgetAveragePerYear.objects.create(year=int(year), value=((bsum/float(vsum)) / float(10.0)) + prixv + rsum + riscvf + pfsum, budget=budget)
                BudgetAveragePerYearRiscs.objects.create(year=int(year), value=((bsum/float(vsum)) / float(10.0)) + prixv + rsum + riscvf + psum + lis_value + riscvs + risceco, budget=budget)
            return obj
        elif validated_data['cc'] and validated_data['pfc'] != None:
            generate_cc_budgets(self, validated_data, obj)
        print 'signature ======== '
        signature(validated_data, temp, obj)
        elapsed = time.time() - start
        print 'time for creatign an offer', elapsed
        return obj



class OfferPfcEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer
        fields = ('id', 'pfc',)

    def update(self, instance, validated_data):
        instance.pfc = validated_data.get('pfc', instance.pfc)
        instance.updated = datetime.now()
        validated_data['name'] = instance.name
        validated_data['cc'] = instance.cc
        validated_data['pfc_market'] = instance.pfc_market
        validated_data['unit'] = instance.unit
        validated_data['lissage_years'] = instance.lissage_years
        validated_data['percent'] = instance.percent
        validated_data['lis_years'] = instance.lis_years
        validated_data['validation_time'] = instance.validation_time
        # print 'valid pfc = ', validated_data
        # print instance
        # print 'try send email data'
        # email_content = self.generate_email_content(obj)
        # TO = Company.objects.get(id=obj.company.id).email
        # FROM ='non.commodity.data@gmail.com'
        # py_mail("Test email subject", email_content, TO, FROM)
        generate_cc_budgets(self, validated_data, instance)
        instance.save()
        return instance


class OfferPfcMEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer
        fields = ('id', 'pfc_market',)

    def update(self, instance, validated_data):
        instance.pfc_market = validated_data.get('pfc_market', instance.pfc_market)
        instance.offer_status = 'confirmer'
        
        majors = defaultdict()
        mparameters = ParameterRecord.objects.filter(offer = instance, parameter=Parameter.objects.get(code='majors')).values('value', 'year')
        for mp in mparameters:
            majors[mp['year']] = mp['value']
        validated_data['majors'] = majors
        validated_data['name'] = instance.name
        validated_data['cc'] = instance.cc
        validated_data['pfc'] = instance.pfc
        validated_data['unit'] = instance.unit
        validated_data['lissage_years'] = instance.lissage_years
        validated_data['lis_years'] = instance.lis_years
        validated_data['percent'] = instance.percent
        validated_data['years'] = instance.years
        validated_data['validation_time'] = instance.validation_time
        # print('instance lissage_years === ', instance.lissage_years, type(instance.lissage_years))
        # print('instance percent === ', instance.percent, type(instance.percent), type(float(instance.percent)))
        # print('validated_data first lissage_years === ', validated_data['lissage_years'], type(validated_data['lissage_years']))
        # print('validated_data first percent === ', validated_data['percent'], type(validated_data['percent']), type(float(instance.percent)))
        temp = copy.copy(validated_data)
        generate_cc_budgets(self, validated_data, instance)
        signature(validated_data, temp, instance)
        instance.updated = datetime.now()
        instance.save()
        return instance


class OfferSignedEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer
        fields = ('id', 'signed_years',)
